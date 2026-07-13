package tools

import (
	"context";
	"github.com/dxh/go-tiny-claw/interface/schema"
)

type Registry interface {
	GetAvailableTools() []schema.ToolDefinition

	Execute(ctx context.Context, call schema.ToolCall) schema.ToolResult
}