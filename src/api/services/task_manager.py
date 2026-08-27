import asyncio
from asyncio import Future
from uuid import UUID, uuid4
from src.common.enums import TaskStatus
from asyncio import CancelledError, InvalidStateError


class TaskManager:
    def __init__(self) -> None:
        self.tasks: dict[
            UUID, dict[UUID, dict[str, TaskStatus | Future[dict[str, str | bool]]]]
        ] = {}

    def add(self, server_id: UUID) -> UUID:
        task_id = uuid4()
        loop = asyncio.get_running_loop()
        if not server_id in self.tasks.keys():
            self.tasks[server_id] = {}
        self.tasks[server_id][task_id] = {
            "status": TaskStatus.PENDING,
            "future": loop.create_future(),
            "accepted_future": loop.create_future(),
        }
        return task_id

    def set_accepted(self, server_id: UUID, task_id: UUID) -> bool:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        self.tasks[server_id][task_id]["status"] = TaskStatus.ACCEPTED

        accepted_future = self.tasks[server_id][task_id]["accepted_future"]
        if not accepted_future.done():
            accepted_future.set_result(True)

        return True

    def set_completed(
        self, server_id: UUID, task_id: UUID, data: dict[str, str | bool]
    ) -> bool:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        if not self.tasks[server_id][task_id]["status"] == TaskStatus.ACCEPTED:
            return False

        self.tasks[server_id][task_id]["status"] = TaskStatus.COMPLETED
        self.tasks[server_id][task_id]["future"].set_result(data)
        return True

    def set_failed(self, server_id: UUID, task_id: UUID, error: str) -> bool:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        if not self.tasks[server_id][task_id]["status"] == TaskStatus.ACCEPTED:
            return False

        self.tasks[server_id][task_id]["status"] = TaskStatus.FAILED
        self.tasks[server_id][task_id]["future"].set_result(error)
        return True

    async def get_result(
        self, server_id: UUID, task_id: UUID
    ) -> None | dict[str, str | bool]:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        task_status = self.tasks[server_id][task_id]["status"]
        task_future = self.tasks[server_id][task_id]["future"]

        if task_status == TaskStatus.FAILED or task_status == TaskStatus.COMPLETED:
            try:
                return task_future.result()
            except CancelledError, InvalidStateError:
                return None

        return None

    async def wait_result(
        self, server_id: UUID, task_id: UUID, timeout: int = 10
    ) -> None | dict[str, str | bool]:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        result = await self.get_result(server_id, task_id)
        if result is not None:
            return result

        try:
            task_future = self.tasks[server_id][task_id]["future"]
            return await asyncio.wait_for(task_future, timeout=timeout)
        except TimeoutError, CancelledError:
            return None

    async def wait_accepted(
        self, server_id: UUID, task_id: UUID, timeout: int = 10
    ) -> bool:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        if self.tasks[server_id][task_id]["status"] != TaskStatus.PENDING:
            return True

        try:
            await asyncio.wait_for(
                self.tasks[server_id][task_id]["accepted_future"], timeout=timeout
            )
            return True
        except TimeoutError, CancelledError:
            return False

    async def remove(self, server_id: UUID, task_id: UUID) -> bool:
        if not server_id in self.tasks.keys():
            return False
        try:
            self.tasks[server_id].pop(task_id)
        except KeyError:
            return False

        return True

    def get_task_status(self, server_id: UUID, task_id: UUID) -> TaskStatus | None:
        if not server_id in self.tasks.keys():
            return False

        if not task_id in self.tasks[server_id].keys():
            return False

        return self.tasks[server_id][task_id]["status"]


task_manager = TaskManager()


def get_task_manager() -> TaskManager:
    return task_manager
