from typing import List
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
        self.db = DB
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
                if user.api_key == api_key:
                    return user
        return None

    def add_user(
        self,
        api_key: str,
        app: str,
        full_access: bool,
        endpoint_access: List[EndpointAccess] | dict | None = None,
    ) -> User | None:
        return self.add_user(api_key, app, full_access, endpoint_access)

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

    def update_user(self, user_id: int, user: User) -> User | None:
        found_user = self.get_user_by_id(user_id)
        if not found_user:
            return None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

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

    def archive_user(self, api_key: str, close_connection: bool = True) -> bool:
        for i in range(len(self.data)):
            if self.data[i].api_key == api_key:
                self.data[i].is_archived = True
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE users
                        SET is_archived = 1
                        WHERE api_key = ?
                    """,
                        (api_key,),
                    )
                # if close_connection:
                #     self.db.commit_and_close()
                return True
        return False

    def unarchive_user(self, api_key: str, close_connection: bool = True) -> bool:
        for i in range(len(self.data)):
            if self.data[i].api_key == api_key:
                self.data[i].is_archived = False
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE users
                        SET is_archived = 0
                        WHERE api_key = ?
                    """,
                        (api_key,),
                    )
                # if close_connection:
                #     self.db.commit_and_close()
                return True
        return False

    def delete_user(self, api_key: str) -> bool:
        if not self.is_user_archived(api_key):
            return False
        user = self.get_user(api_key)
        if not user:
            return False
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM endpoint_access
                WHERE user_id = ?
            """,
                (user.id,),
            )
            conn.commit()

            cursor.execute(
                """
                DELETE FROM users
                WHERE api_key = ?
            """,
                (api_key,),
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

    def is_user_archived(self, api_key: str) -> bool | None:
        user = self.get_user(api_key)
        if user:
            return user.is_archived
