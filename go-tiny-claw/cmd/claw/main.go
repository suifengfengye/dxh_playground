package main

import (
	"fmt"
	"log"

	"github.com/dxh/go-tiny-claw/internal/provider"
	"github.com/dxh/go-tiny-claw/internal/tools"
)

type AgentEngine struct {
	Provider provider.LLMProvider
	Registry tools.Registry

	// 工作路径
	WorkDir string
}

func NewAgentEngine(provider provider.LLMProvider, registry tools.Registry, WorkDir string) *AgentEngine{
	return &AgentEngine{
		Provider: provider,
		Registry: registry,
		WorkDir: WorkDir,
	}
}

func main(){
	fmt.Println("🚀欢迎来动 go-tiny-claw 的启动程序")
	// 1. Provider
	// provider := provider.NewClaudeProvider()
	// 2. context
	// ctxManager := context.NewManager()
	// 3. tools
	// register := tools.NewRegister()
	// engine := engine.NewAgentEngine(provider, ctxManager, register)
	// err := engine.Run()
	// if err != nil {
	// 	fmt.Println("启动失败, %v", err)
	// }
	log.Println("架构蓝图启动完毕")
}