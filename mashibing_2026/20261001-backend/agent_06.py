import base64
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import BackendProtocol
from deepagents.backends.protocol import (
    DeleteResult,
    EditResult,
    FileData,
    FileDownloadResponse,
    FileInfo,
    FileUploadResponse,
    GlobResult,
    GrepResult,
    LsResult,
    ReadResult,
    WriteResult,
)
from deepagents.backends.utils import (
    InvalidGlobPatternError,
    _copy_file_data_with_content,
    _get_backend_read_file_type,
    _glob_search_files,
    create_file_data,
    file_data_to_string,
    grep_matches_from_files,
    perform_string_replacement,
    slice_read_response,
    update_file_data,
    validate_path,
)
from langgraph.store.memory import InMemoryStore

from llm import ds_llm


class DictBackend(BackendProtocol):
    """把文件全部存进一个普通 Python 字典的 Backend。

    `self.data` 的结构是 `{绝对路径: FileData}`：

    - 文件：`{"content": str, "encoding": str, "created_at": str, "modified_at": str}`
    - 目录：`{}`（空字典占位，根目录 `/` 默认就有一个）

    和内置的 `StateBackend` 相比，它不依赖 LangGraph 的 state / config，
    在图外面也能直接读写，方便调试和写单测。

    用法::

        backend = DictBackend({"/a.txt": "hello"})  # 初始化时预置文件
        backend = DictBackend({"/a.txt": {"content": "hello", "encoding": "utf-8"}})  # 也接受完整 FileData
        backend.write("/dir/b.txt", "world")        # 之后写入的文件同样落在 data 里
        backend.read("/a.txt")
    """

    def __init__(self, files: dict[str, str | FileData] | None = None):
        self.data: dict[str, Any] = {}
        self.data["/"] = {}
        for path, content in (files or {}).items():
            self.data[validate_path(path)] = self._to_file_data(content)

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    @staticmethod
    def _to_file_data(value: Any) -> FileData:
        """把初始化传入的值统一成 FileData。

        允许两种写法：内容字符串，或完整的 FileData。
        注意别写成 `{"/a.txt": {"content": "..."}}` 又指望它是内容字符串——
        那样会嵌套成 `{"content": {"content": "..."}}`，读取时直接 TypeError。
        """
        if isinstance(value, dict):
            if "content" not in value:
                msg = f"文件内容要么是字符串，要么是带 content 键的 FileData，收到：{value!r}"
                raise TypeError(msg)
            return create_file_data(
                value["content"],
                created_at=value.get("created_at"),
                encoding=value.get("encoding", "utf-8"),
            )
        return create_file_data(value)

    @staticmethod
    def _is_file(value: Any) -> bool:
        """目录占位是空字典，只有带 content 的才算文件。"""
        return isinstance(value, dict) and "content" in value

    def _files(self) -> dict[str, Any]:
        """只返回文件，过滤掉目录占位。

        `grep_matches_from_files` / `_glob_search_files` 会直接读 `file_data["content"]`，
        目录占位放进去会 KeyError。
        """
        return {path: fd for path, fd in self.data.items() if self._is_file(fd)}

    # ------------------------------------------------------------------
    # BackendProtocol 接口
    # ------------------------------------------------------------------

    def ls(self, path: str) -> LsResult:
        """列出某个目录下的直接子项（不递归）。"""
        base = "/" if path in ("", "/") else path.rstrip("/")
        prefix = "/" if base == "/" else base + "/"

        entries: list[FileInfo] = []
        subdirs: set[str] = set()

        for key, value in self.data.items():
            if key == base or not key.startswith(prefix):
                continue
            relative = key[len(prefix):]
            if not relative:
                continue
            if "/" in relative:
                # 还嵌套着更深层级，只记下第一层子目录
                subdirs.add(prefix + relative.split("/", 1)[0] + "/")
            elif self._is_file(value):
                entries.append(
                    {
                        "path": key,
                        "is_dir": False,
                        "size": len(file_data_to_string(value).encode("utf-8")),
                        "modified_at": value.get("modified_at", ""),
                    }
                )
            else:
                # 显式登记过、且当前为空的目录
                subdirs.add(key.rstrip("/") + "/")

        entries.extend({"path": subdir, "is_dir": True, "size": 0, "modified_at": ""} for subdir in sorted(subdirs))
        entries.sort(key=lambda info: info["path"])
        return LsResult(entries=entries)

    def read(
        self,
        file_path: str,
        offset: int = 0,
        limit: int = 2000,
    ) -> ReadResult:
        """按行区间读取文件，返回未格式化的原始内容。"""
        file_data = self.data.get(file_path)
        if not self._is_file(file_data):
            return ReadResult(error=f"File '{file_path}' not found")

        if _get_backend_read_file_type(file_path) != "text":
            # 二进制文件直接返回内容字符串（base64），不做行切片
            return ReadResult(file_data=_copy_file_data_with_content(file_data, file_data_to_string(file_data)))

        return slice_read_response(file_data, offset, limit)

    def write(
        self,
        file_path: str,
        content: str,
    ) -> WriteResult:
        """写入文件，已存在则覆盖（保留 created_at）。"""
        existing = self.data.get(file_path)
        if self._is_file(existing):
            self.data[file_path] = update_file_data(existing, content)
        else:
            self.data[file_path] = create_file_data(content)
        return WriteResult(path=file_path)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,  # noqa: FBT001, FBT002
    ) -> EditResult:
        """精确字符串替换；默认要求 old_string 在文件中唯一。"""
        file_data = self.data.get(file_path)
        if not self._is_file(file_data):
            return EditResult(error=f"Error: File '{file_path}' not found")

        result = perform_string_replacement(file_data_to_string(file_data), old_string, new_string, replace_all)
        if isinstance(result, str):
            return EditResult(error=result)

        new_content, occurrences = result
        self.data[file_path] = update_file_data(file_data, new_content)
        return EditResult(path=file_path, occurrences=int(occurrences))

    def delete(self, file_path: str) -> DeleteResult:
        """删除文件或目录（递归删除其下的所有内容）。

        根目录 `/` 本身不会被删掉，只会清空它下面的文件。
        """
        base = file_path.rstrip("/") or "/"
        prefix = "/" if base == "/" else base + "/"

        to_delete = [key for key in self.data if key == base or key.startswith(prefix)]
        if base == "/":
            to_delete = [key for key in to_delete if key != "/"]
        if not to_delete:
            return DeleteResult(error=f"Error: File '{file_path}' not found")

        for key in to_delete:
            del self.data[key]
        return DeleteResult(path=file_path)

    def grep(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        *,
        max_count: int | None = None,
    ) -> GrepResult:
        """字面量（非正则）全文搜索。"""
        return grep_matches_from_files(
            self._files(),
            pattern,
            path if path is not None else "/",
            glob,
            max_count=max_count,
        )

    def glob(self, pattern: str, path: str | None = None) -> GlobResult:
        """按 glob 匹配文件路径。"""
        try:
            result = _glob_search_files(self._files(), pattern, path)
        except InvalidGlobPatternError as exc:
            # glob 是工具边界，非法 pattern 返回结果而不是抛异常
            return GlobResult(error=str(exc))

        if result == "No files found":
            return GlobResult(matches=[])

        infos: list[FileInfo] = []
        for file_path in result.split("\n"):
            fd = self.data.get(file_path) or {}
            infos.append(
                {
                    "path": file_path,
                    "is_dir": False,
                    "size": len(file_data_to_string(fd).encode("utf-8")) if fd else 0,
                    "modified_at": fd.get("modified_at", ""),
                }
            )
        return GlobResult(matches=infos)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """批量上传（二进制内容自动转 base64）。"""
        responses: list[FileUploadResponse] = []
        for path, content in files:
            try:
                text = content.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text = base64.b64encode(content).decode("ascii")
                encoding = "base64"

            existing = self.data.get(path)
            created_at = existing.get("created_at") if self._is_file(existing) else None
            self.data[path] = create_file_data(text, created_at=created_at, encoding=encoding)
            responses.append(FileUploadResponse(path=path, error=None))
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """批量下载，逐条返回成功或错误，便于部分成功。"""
        responses: list[FileDownloadResponse] = []
        for path in paths:
            file_data = self.data.get(path)
            if not self._is_file(file_data):
                responses.append(FileDownloadResponse(path=path, content=None, error="file_not_found"))
                continue

            content_str = file_data_to_string(file_data)
            encoding = file_data.get("encoding", "utf-8")
            content_bytes = content_str.encode("utf-8") if encoding == "utf-8" else base64.standard_b64decode(content_str)
            responses.append(FileDownloadResponse(path=path, content=content_bytes, error=None))
        return responses


agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=DictBackend({"/a.txt": "1234567890"}),
    store=InMemoryStore()
)
