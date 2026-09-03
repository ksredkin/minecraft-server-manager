import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID


@dataclass
class Reservation:
    total: int
    processed: int


class StorageService:
    def __init__(self) -> None:
        self._reservations: dict[UUID, Reservation] = {}

    def get_disk_free_space(self, path: Path) -> int:
        usage = shutil.disk_usage(path.root)
        return usage.free

    def get_reserved(self) -> int:
        return sum(
            [
                reservation.total - reservation.processed
                for reservation in self._reservations.values()
            ]
        )

    def reserve(self, path: Path, reservation_id: UUID, size: int) -> bool:
        free_space = self.get_disk_free_space(path)
        reserved = self.get_reserved()
        if (free_space - reserved) < size:
            return False

        self._reservations[reservation_id] = Reservation(size, 0)
        return True

    def remove_reservation(self, reservation_id: UUID) -> None:
        self._reservations.pop(reservation_id)

    def add_progress(self, reservation_id: UUID, progress: int) -> None:
        reservation = self._reservations.get(reservation_id)
        if not reservation:
            return

        reservation.processed += progress

    def get_progress(self, reservation_id: UUID) -> int | None:
        reservation = self._reservations.get(reservation_id)
        if not reservation:
            return None

        return reservation.processed


storage_service = StorageService()


def get_storage_service() -> StorageService:
    return storage_service
