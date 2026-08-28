import asyncio
from asyncio import CancelledError, Future, InvalidStateError
from dataclasses import dataclass
from uuid import UUID, uuid4

from src.common.enums import TaskStatus


@dataclass
class Task:
    status: TaskStatus
    future: Future[dict[str, str | bool]]
    accepted_future: Future[bool | dict[str, str]]

    total: int | None = None
    processed: int = 0


class TaskManager:
    def __init__(self) -> None:
        self.tasks: dict[UUID, dict[UUID, Task]] = {}
        self.task_to_server: dict[UUID, UUID] = {}

    def add(self, server_id: UUID) -> UUID:
        task_id = uuid4()
        loop = asyncio.get_running_loop()
        if server_id not in self.tasks.keys():
            self.tasks[server_id] = {}
        self.tasks[server_id][task_id] = Task(
            TaskStatus.PENDING, loop.create_future(), loop.create_future()
        )
        self.task_to_server[task_id] = server_id
        return task_id

    def set_accepted(
        self,
        server_id: UUID,
        task_id: UUID,
        data: dict[str, str | bool] = {"success": True},
    ) -> bool:
        if server_id not in self.tasks.keys():
            return False

        if task_id not in self.tasks[server_id].keys():
            return False

        self.tasks[server_id][task_id].status = TaskStatus.ACCEPTED

        accepted_future = self.tasks[server_id][task_id].accepted_future
        if not accepted_future.done():
            accepted_future.set_result(data)

        return True

    def set_completed(
        self, server_id: UUID, task_id: UUID, data: dict[str, str | bool]
    ) -> bool:
        if server_id not in self.tasks.keys():
            return False

        if task_id not in self.tasks[server_id].keys():
            return False

        if not self.tasks[server_id][task_id].status == TaskStatus.ACCEPTED:
            return False

        self.tasks[server_id][task_id].status = TaskStatus.COMPLETED
        self.tasks[server_id][task_id].future.set_result(data)
        return True

    def set_failed(self, server_id: UUID, task_id: UUID, error: str) -> bool:
        if server_id not in self.tasks.keys():
            return False

        if task_id not in self.tasks[server_id].keys():
            return False

        if not self.tasks[server_id][task_id].status == TaskStatus.ACCEPTED:
            return False

        self.tasks[server_id][task_id].status = TaskStatus.FAILED
        self.tasks[server_id][task_id].future.set_result(error)
        return True

    async def get_result(
        self, server_id: UUID, task_id: UUID
    ) -> dict[str, str | bool] | None:
        if server_id not in self.tasks.keys():
            return None

        if task_id not in self.tasks[server_id].keys():
            return None

        task_status = self.tasks[server_id][task_id].status
        task_future = self.tasks[server_id][task_id].future

        if task_status == TaskStatus.FAILED or task_status == TaskStatus.COMPLETED:
            try:
                return task_future.result()
            except CancelledError, InvalidStateError:
                return None

        return None

    async def wait_result(
        self, server_id: UUID, task_id: UUID, timeout: int = 10
    ) -> None | dict[str, str | bool]:
        if server_id not in self.tasks.keys():
            return False

        if task_id not in self.tasks[server_id].keys():
            return False

        result = await self.get_result(server_id, task_id)
        if result is not None:
            return result

        try:
            task_future = self.tasks[server_id][task_id].future
            return await asyncio.wait_for(task_future, timeout=timeout)
        except TimeoutError, CancelledError:
            return None

    async def wait_accepted(
        self, server_id: UUID, task_id: UUID, timeout: int = 10
    ) -> dict[str, str]:
        if server_id not in self.tasks.keys():
            return {"success": False}

        if task_id not in self.tasks[server_id].keys():
            return {"success": False}

        if self.tasks[server_id][task_id].status != TaskStatus.PENDING:
            return {"success": True}

        try:
            return await asyncio.wait_for(
                self.tasks[server_id][task_id].accepted_future, timeout=timeout
            )
        except TimeoutError, CancelledError:
            return {"success": False}

    async def remove(self, server_id: UUID, task_id: UUID) -> bool:
        if server_id not in self.tasks.keys():
            return False
        try:
            self.tasks[server_id].pop(task_id)
            self.task_to_server.pop(task_id)
        except KeyError:
            return False

        return True

    def get_task_status(self, server_id: UUID, task_id: UUID) -> TaskStatus | None:
        if server_id not in self.tasks.keys():
            return False

        if task_id not in self.tasks[server_id].keys():
            return False

        return self.tasks[server_id][task_id].status

    def get_server_id_by_task(self, task_id: UUID) -> UUID | None:
        return self.task_to_server.get(task_id, None)

    def set_task_total(
        self,
        server_id: UUID,
        task_id: UUID,
        total: int,
    ) -> bool:
        task = self.tasks.get(server_id, {}).get(task_id)

        if not task:
            return False

        task.total = total
        return True

    def set_task_processed(
        self,
        server_id: UUID,
        task_id: UUID,
        processed: int,
    ) -> bool:
        task = self.tasks.get(server_id, {}).get(task_id)

        if not task:
            return False

        task.processed = processed
        return True

    def add_progress(
        self,
        server_id: UUID,
        task_id: UUID,
        progress: int,
    ) -> bool:
        task = self.tasks.get(server_id, {}).get(task_id)

        if not task:
            return False

        task.processed += progress
        return True

    def get_task_completion_percent(self, server_id: UUID, task_id: UUID) -> int | None:
        task = self.tasks.get(server_id, {}).get(task_id)

        if not task:
            return None

        return task.processed / task.total * 100


task_manager = TaskManager()


def get_task_manager() -> TaskManager:
    return task_manager
