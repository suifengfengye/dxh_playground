package schema

import "encoding/json"

// 1. 定义 Role 类型
type Role string

// 2. 定义 Role 相关常量
const (
	RoleSystem Role = "system"        // system 角色常量
	RoleUser Role = "user"            // user 角色常量
	RoleAssistant Role = "assistant"  // assistant 角色常量
)

// 3. 定义 Message 结构体
type Message struct {
	Role Role `json:"role"`
	Content string `json:"content"`
	ToolCalls []ToolCall `json:"tool_class,omitempty"`
	ToolCallID string `json:"tool_call_id,omitempty"`
}

// 4. 定义 TooCall 结构体
type ToolCall struct{
	ID string `json:"id"`
	Name string `json:"name"`
	Arguments json.RawMessage `json:"arguments"`
}
// 5. 定义 ToolResult 结构体
type ToolResult struct {
	ToolCallID string `json:"tool_call_id"`
	Output string `json:"output"`
	IsError bool `json:"is_error"`
}

// 6. 定义 ToolDefinition 结构体
type ToolDefinition struct {
	Name string `json:"name"`
	Description string `json:"description"`
	InputSchema interface{} `json:"input_schema"`
}