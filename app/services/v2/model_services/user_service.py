from typing import List
from services.v2 import data_provider_v2
from models.v2.endpoint_access import EndpointAccess
from models.v2.user import User
from services.v2.base_service import Base
from utils.globals import *
from datetime import datetime, timedelta
from services.v2.database_service import DB
from utils.globals import cache_time_minutes

USERS = []


class UserService(Base):
    def __init__(self, is_debug: bool = False):
        self.db = data_provider_v2.fetch_database()
        self.last_updated = datetime.now()
        self.data = []
        self.load(is_debug)

    def get_all_users(self) -> List[User]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM users
            """
            )
            users = cursor.fetchall()

            users_list = []
            for user_id, api_key, app, full_access, is_archived in users:
                cursor.execute(
                    """
                    SELECT endpoint, full, can_get, can_post, can_put, can_delete
                    FROM endpoint_access
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                endpoints = cursor.fetchall()

                endpoint_access = []
                for (
                    endpoint,
                    full,
                    can_get,
                    can_post,
                    can_put,
                    can_delete,
                ) in endpoints:
                    endpoint_access.append(
                        EndpointAccess(
                            endpoint=endpoint,
                            full=full,
                            get=bool(can_get),
                            post=bool(can_post),
                            put=bool(can_put),
                            delete=bool(can_delete),
                        )
                    )

                users_list.append(
                    User(
                        id=user_id,
                        api_key=api_key,
                        app=app,
                        full=full_access,
                        endpoint_access=endpoint_access,
                        is_archived=is_archived,
                    )
                )

        return users_list

    def get_users(self) -> List[User]:
        users = []
        for user in self.data:
            if not user.is_archived:
                users.append(user)
        return users

    def get_user(self, api_key: str, need_from_db: bool = False) -> User | None:
        if (
            need_from_db
            or self.last_updated
            < datetime.now() - timedelta(minutes=cache_time_minutes)
            or not self.data
        ):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE api_key = ?
                """,
                    (api_key,),
                )
                user_row = cursor.fetchone()

                if not user_row:
                    return None

                user_id, api_key, app, full_access, is_archived = user_row
                full_access = bool(full_access)

                cursor.execute(
                    """
                    SELECT endpoint, full, can_get, can_post, can_put, can_delete
                    FROM endpoint_access
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                endpoints = cursor.fetchall()

                endpoint_access = []
                for endpoint, full, can_get, can_post, can_put, can_delete in endpoints:
                    endpoint_access.append(
                        EndpointAccess(
                            endpoint=endpoint,
                            full=full,
                            get=bool(can_get),
                            post=bool(can_post),
                            put=bool(can_put),
                            delete=bool(can_delete),
                        )
                    )

            return User(
                id=user_id,
                api_key=api_key,
                app=app,
                full=full_access,
                endpoint_access=endpoint_access,
                is_archived=is_archived,
            )
        else:
            for user in self.data:
                if user.api_key == api_key:
                    return user
        return None

    def get_user_by_id(self, id: int, need_from_db: bool = False) -> User | None:
        if (
            need_from_db
            or self.last_updated
            < datetime.now() - timedelta(minutes=cache_time_minutes)
            or not self.data
        ):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE id = ?
                """,
                    (id,),
                )
                user_row = cursor.fetchone()

                if not user_row:
                    return None

                user_id, api_key, app, full_access, is_archived = user_row
                full_access = bool(full_access)

                cursor.execute(
                    """
                    SELECT endpoint, full, can_get, can_post, can_put, can_delete
                    FROM endpoint_access
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                endpoints = cursor.fetchall()

                endpoint_access = []
                for endpoint, full, can_get, can_post, can_put, can_delete in endpoints:
                    endpoint_access.append(
                        EndpointAccess(
                            endpoint=endpoint,
                            full=full,
                            get=bool(can_get),
                            post=bool(can_post),
                            put=bool(can_put),
                            delete=bool(can_delete),
                        )
                    )

            return User(
                id=user_id,
                api_key=api_key,
                app=app,
                full=full_access,
                endpoint_access=endpoint_access,
                is_archived=is_archived,
            )
        else:
            for user in self.data:
                if user.id == id:
                    return user
        return None

    def add_new_user(self, user: User) -> User | None:
        return self.add_user(user.api_key, user.app, user.full, user.endpoint_access)

    def add_user(
        self,
        api_key: str,
        app: str,
        full_access: bool,
        endpoint_access: List[EndpointAccess] | dict | None = None,
    ) -> User | None:
        if self.get_user(api_key):
            return None
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (api_key, app, full_access, is_archived)
                VALUES (?, ?, ?, ?)
            """,
                (api_key, app, full_access, False),
            )
            conn.commit()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE api_key = ?
            """,
                (api_key,),
            )
            added_id = cursor.fetchone()[0]

            if endpoint_access:
                if isinstance(endpoint_access, dict):
                    for endpoint, access in endpoint_access.items():
                        if not access:
                            continue

                        cursor.execute(
                            """
                            INSERT INTO endpoint_access (user_id, endpoint, full, can_get, can_post, can_put, can_delete)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                added_id,
                                endpoint,
                                access["full"],
                                access["get"],
                                access["post"],
                                access["put"],
                                access["delete"],
                            ),
                        )
                        conn.commit()
                elif isinstance(endpoint_access, list):
                    for access in endpoint_access:
                        if not access:
                            continue
                        cursor.execute(
                            """
                            INSERT INTO endpoint_access (user_id, endpoint, full, can_get, can_post, can_put, can_delete)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                added_id,
                                access.endpoint,
                                access.full,
                                access.get,
                                access.post,
                                access.put,
                                access.delete,
                            ),
                        )
                        conn.commit()

        added_user = self.get_user(api_key, True)
        self.data.append(added_user)
        return added_user

    def update_user(
        self, user_id: int, user: User, is_archived: bool | None = None
    ) -> User | None:
        found_user = self.get_user_by_id(user_id)
        if not found_user:
            return None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            if is_archived is not None:
                cursor.execute(
                    """
                    UPDATE users
                    SET api_key = ?, app = ?, full_access = ?, is_archived = ?
                    WHERE id = ?
                """,
                    (user.api_key, user.app, user.full, is_archived, user_id),
                )
            else:
                cursor.execute(
                    """
                UPDATE users
                SET api_key = ?, app = ?, full_access = ?
                WHERE id = ?
                """,
                    (user.api_key, user.app, user.full, user_id),
                )
            conn.commit()

            for access in user.endpoint_access:
                if access not in found_user.endpoint_access:
                    if access.endpoint in [
                        a.endpoint for a in found_user.endpoint_access
                    ]:
                        cursor.execute(
                            """
                            UPDATE endpoint_access
                            SET full = ?, can_get = ?, can_post = ?, can_put = ?, can_delete = ?
                            WHERE user_id = ? AND endpoint = ?
                        """,
                            (
                                access.full,
                                access.get,
                                access.post,
                                access.put,
                                access.delete,
                                user_id,
                                access.endpoint,
                            ),
                        )
                        conn.commit()
                    else:
                        cursor.execute(
                            """
                            INSERT INTO endpoint_access (user_id, endpoint, full, can_get, can_post, can_put, can_delete)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                user_id,
                                access.endpoint,
                                access.full,
                                access.get,
                                access.post,
                                access.put,
                                access.delete,
                            ),
                        )
                        conn.commit()

            for access in found_user.endpoint_access:
                if access not in user.endpoint_access:
                    cursor.execute(
                        """
                        DELETE FROM endpoint_access
                        WHERE user_id = ? AND endpoint = ?
                    """,
                        (user_id, access.endpoint),
                    )
                    conn.commit()

        updated_user = self.get_user(user.api_key, True)
        for i in range(len(self.data)):
            if self.data[i].id == user_id:
                self.data[i] = updated_user
        return updated_user

    def archive_user(self, id: int) -> User | None:
        for i in range(len(self.data)):
            if self.data[i].id == id:
                self.data[i].is_archived = True
                return self.update_user(id, self.data[i], True)
        return None

    def unarchive_user(self, id: int) -> User | None:
        for i in range(len(self.data)):
            if self.data[i].id == id:
                self.data[i].is_archived = False
                return self.update_user(id, self.data[i], False)
        return None

    def delete_user(self, user_id: int) -> bool:
        if not self.is_user_archived(user_id):
            return False
        user = self.get_user(user_id)
        if not user:
            return False
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM endpoint_access
                WHERE user_id = ?
            """,
                (user_id,),
            )
            conn.commit()

            cursor.execute(
                """
                DELETE FROM users
                WHERE id = ?
            """,
                (user_id,),
            )
            conn.commit()
        self.data.remove(user)
        return True

    def load(self, is_debug: bool):
        if is_debug:
            self.data = USERS
        else:  # pragma: no cover
            self.data = self.get_all_users()

    def has_access(self, api_key: str, path: str, method: str) -> bool:
        user = self.get_user(api_key)
        if user.full:
            return True
        else:
            for access in user.endpoint_access:
                if access.endpoint == path:
                    if access.full:
                        return True
                    return getattr(access, method)
            return False

    def is_user_archived(self, id: int) -> bool | None:
        user = self.get_user_by_id(id)
        if user:
            return user.is_archived
