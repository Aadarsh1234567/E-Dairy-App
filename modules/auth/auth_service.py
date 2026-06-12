"""
Authentication service — bilingual error messages via translations.t().
"""
import bcrypt
from datetime import datetime, timedelta
from database.database import get_session, get_setting, set_setting, write_audit_log

DEFAULT_PASSWORD      = "admin123"
MAX_ATTEMPTS          = 3
LOCKOUT_MINUTES       = 5
SETTINGS_KEY_HASH     = "password_hash"
SETTINGS_KEY_ATTEMPTS = "failed_attempts"
SETTINGS_KEY_LOCKOUT  = "lockout_until"
SETTINGS_KEY_FIRST    = "is_first_login"


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class AuthError(Exception):
    pass

class AccountLockedError(AuthError):
    def __init__(self, locked_until: datetime):
        self.locked_until = locked_until
        remaining = max(0, int((locked_until - datetime.utcnow()).total_seconds()))
        m, s = divmod(remaining, 60)
        super().__init__(_t("locked_countdown", m=m, s=s))

class WrongPasswordError(AuthError):
    def __init__(self, remaining: int):
        self.remaining = remaining
        super().__init__(_t("invalid_password") +
                         (f" ({remaining} attempts remaining)" if remaining > 0 else ""))


def is_first_login() -> bool:
    return get_setting(SETTINGS_KEY_FIRST, "1") == "1"


def is_locked() -> tuple[bool, datetime | None]:
    lockout_str = get_setting(SETTINGS_KEY_LOCKOUT, "")
    if not lockout_str:
        return False, None
    try:
        until = datetime.fromisoformat(lockout_str)
        if datetime.utcnow() < until:
            return True, until
        _clear_lockout()
        return False, None
    except ValueError:
        _clear_lockout()
        return False, None


def verify_password(plain: str) -> bool:
    locked, until = is_locked()
    if locked:
        raise AccountLockedError(until)

    stored_hash = get_setting(SETTINGS_KEY_HASH, "")
    if stored_hash:
        match = bcrypt.checkpw(plain.encode("utf-8"), stored_hash.encode("utf-8"))
    else:
        match = (plain == DEFAULT_PASSWORD)

    if match:
        _on_success()
        return True
    else:
        _on_failure()
        attempts = int(get_setting(SETTINGS_KEY_ATTEMPTS, "0"))
        remaining = max(0, MAX_ATTEMPTS - attempts)
        raise WrongPasswordError(remaining)


def change_password(old_plain: str, new_plain: str, confirm_plain: str) -> None:
    if new_plain != confirm_plain:
        raise AuthError(_t("pw_no_match"))
    if len(new_plain) < 6:
        raise AuthError(_t("pw_too_short"))
    if new_plain == DEFAULT_PASSWORD:
        raise AuthError(_t("pw_default_reuse"))

    verify_password(old_plain)

    hashed = bcrypt.hashpw(new_plain.encode("utf-8"), bcrypt.gensalt(rounds=12))
    set_setting(SETTINGS_KEY_HASH,     hashed.decode("utf-8"))
    set_setting(SETTINGS_KEY_FIRST,    "0")
    set_setting(SETTINGS_KEY_ATTEMPTS, "0")
    set_setting(SETTINGS_KEY_LOCKOUT,  "")
    with get_session() as session:
        write_audit_log(session, "PASSWORD_CHANGED", "Operator changed login password")
        session.commit()


def get_idle_lock_minutes() -> int:
    try:
        return int(get_setting("idle_lock_minutes", "15"))
    except ValueError:
        return 15


def _on_success():
    set_setting(SETTINGS_KEY_ATTEMPTS, "0")
    set_setting(SETTINGS_KEY_LOCKOUT,  "")


def _on_failure():
    attempts = int(get_setting(SETTINGS_KEY_ATTEMPTS, "0")) + 1
    set_setting(SETTINGS_KEY_ATTEMPTS, str(attempts))
    if attempts >= MAX_ATTEMPTS:
        until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        set_setting(SETTINGS_KEY_LOCKOUT, until.isoformat())
        with get_session() as session:
            write_audit_log(session, "ACCOUNT_LOCKED",
                f"Account locked after {MAX_ATTEMPTS} failed attempts. "
                f"Until {until.strftime('%H:%M:%S UTC')}.")
            session.commit()


def _clear_lockout():
    set_setting(SETTINGS_KEY_LOCKOUT,  "")
    set_setting(SETTINGS_KEY_ATTEMPTS, "0")
