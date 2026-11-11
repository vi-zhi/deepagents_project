from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from config import MODEL_NAME
from context_type import MemoryContext
from contextlib import ExitStack


load_dotenv()
default_backend = StateBackend()

stack = ExitStack()

checkpointer = stack.enter_context(PostgresSaver.from_conn_string("postgres://postgres:123456@localhost:5432/deepagents"))
store = stack.enter_context(PostgresStore.from_conn_string(conn_string="postgres://postgres:123456@localhost:5432/deepagents"))

checkpointer.setup()
store.setup()
#
agent = create_deep_agent(
    model=MODEL_NAME,
    context_schema=MemoryContext,
    memory=["/memory/AGENTS.md", "/memory/habits.md"],
    skills=["/skill/"],
    checkpointer=checkpointer,
    backend=CompositeBackend(
        default=default_backend,
        routes={
            "/memories/AGENTS.md": StoreBackend(
                namespace=lambda _rt:("123",),
                store=store,
            ),
            "/memories/habits.md": StoreBackend(
                namespace=lambda _rt:("123",),
                store=store,
            ),
            "/skills/": FilesystemBackend(
                root_dir=str("/"),
                virtual_mode=True,
            ),
        }
    )
)

stack.close()
