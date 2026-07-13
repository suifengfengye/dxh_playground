package main

import (
	"fmt";
	"encoding/json";
	"github.com/dxh/go-tiny-claw/internal/schema"
)

func main(){
	message := schema.Message{
		Role: schema.RoleUser,
		Content: "海阔天空！！！",
	}

	data, err := json.Marshal(message)
	if err != nil {
		fmt.Println("marshal err:", err)
		return
	}

	fmt.Println("✅ test", string(data))
	// 2. string 转为 结构体
	value := `{"role":"assistant","content":"您问到了重点！"}`
	var msg2 schema.Message
	err2 := json.Unmarshal([]byte(value), &msg2)
	if err2 != nil {
		fmt.Println("unmarshal error:", err2)
		return
	}
	// 3.
	var content string = "testvar"
	fmt.Println(content)
}