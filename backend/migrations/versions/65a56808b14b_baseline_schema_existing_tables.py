"""baseline schema (existing tables)

基线迁移：纯记录点，不执行任何 DDL。
当前库结构由 SQLModel 的 create_all 建立；两张遗留表
reader_users / room_chat_messages 不在 models 中，刻意保留、不交给 Alembic 管理。
后续的表结构变更请用 `alembic revision --autogenerate` 生成后再人工审阅。

Revision ID: 65a56808b14b
Revises:
Create Date: 2026-10-12 12:29:15.164750

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '65a56808b14b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
