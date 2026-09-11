import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from src.common.enums import DaemonTaskKind
from src.daemon.exceptions.storage_service import (
    ReservationNotFoundError,
    StorageAccessError,
)


@dataclass
class Reservation:
    server_key: str
    kind: DaemonTaskKind
    name: str
    total: int
    processed: int


class StorageService:
    def __init__(self) -> None:
        self._reservations: dict[UUID, Reservation] = {}

    def get_disk_free_space(self, path: Path) -> int:
        try:
            return shutil.disk_usage(path.anchor or path.resolve().anchor).free
        except OSError as error:
            raise StorageAccessError(
                f'Cannot get free space for "{path}".'
            ) from error

    def get_reserved(self) -> int:
        return sum(
            [
                reservation.total - reservation.processed
                for reservation in self._reservations.values()
            ]
        )

    def reserve(
        self,
        path: Path,
        reservation_id: UUID,
        size: int,
        server_key: str,
        kind: DaemonTaskKind,
        name: str,
    ) -> bool:
        free_space = self.get_disk_free_space(path)
        reserved = self.get_reserved()
        if (free_space - reserved) < size:
            return False

        self._reservations[reservation_id] = Reservation(
            server_key, kind, name, size, 0
        )
        return True

    def remove_reservation(self, reservation_id: UUID) -> None:
        self._reservations.pop(reservation_id, None)

    def _get_reservation(self, reservation_id: UUID) -> Reservation:
        reservation = self._reservations.get(reservation_id)
        if not reservation:
            raise ReservationNotFoundError("Reservation not found.")
        return reservation

    def add_progress(self, reservation_id: UUID, progress: int) -> None:
        reservation = self._get_reservation(reservation_id)
        reservation.processed += progress

    def get_progress(self, reservation_id: UUID) -> int | None:
        reservation = self._get_reservation(reservation_id)
        return reservation.processed

    def is_complete(self, reservation_id: UUID) -> bool:
        reservation = self._get_reservation(reservation_id)
        return reservation.processed >= reservation.total

    def get_tasks(self, server_key: str) -> dict[str, dict[str, dict[str, int]]]:
        tasks: dict[str, dict[str, dict[str, int]]] = {
            "backups": {},
            "plugins": {},
        }

        for reservation in self._reservations.values():
            if reservation.server_key != server_key:
                continue

            tasks.setdefault(reservation.kind.value, {})[reservation.name] = {
                "total": reservation.total,
                "processed": reservation.processed,
            }

        return tasks
