from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from config import MODEL_NAME
from context_type import MemoryContext


default_backend = StateBackend()

with PostgresSaver.from_conn_string("postgres://postgres:root@localhost:5432/deepagents") as checkpointer,\
     PostgresStore.from_conn_string(conn_string="postgres://postgres:root@localhost:5432/deepagents") as store:
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
                    namespace=lambda _rt:123,
                    store=store,
                ),
                "/memories/habits.md": StoreBackend(
                    namespace=lambda _rt:123,
                    store=store,
                ),
                "/skills/": FilesystemBackend(
                    root_dir=str("/"),
                    virtual_mode=True,
                ),
            }
        )
    )
