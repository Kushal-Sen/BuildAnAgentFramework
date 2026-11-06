"""whitebox: an agent framework you can see inside."""
from .agent import Agent, Event, Result
from .messages import Message, ToolCall
from .models import FakeModel, Model, ModelError, OllamaModel, load_model
from .tools import Tool, Toolbox, tool
from .hooks import Approval, Hook, Printer, Tracer, show_trace
from .reliability import Fallback, LoopGuard, RescueToolCalls, Retry, with_timeout
from .evals import (
    Case, Check, Report, compare, contains, excludes, finished, judged, load_report, run_eval, tools_used,
    used_no_tools, used_tool,
)
from .rag import (
    ChromaStore, Chunk, Embedder, FakeEmbedder, Hit, Index, OllamaEmbedder, VectorStore, cosine, load_documents,
)
