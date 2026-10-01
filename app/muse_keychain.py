"""Small macOS Keychain generic-password bridge with no secret in argv/env."""

from __future__ import annotations

import ctypes
import ctypes.util
from pathlib import Path
from typing import Optional


_Void = ctypes.c_void_p
_UInt = ctypes.c_uint32


def _frameworks():
    security_path = ctypes.util.find_library("Security")
    core_path = ctypes.util.find_library("CoreFoundation")
    if not security_path or not core_path:
        raise OSError("macos_keychain_unavailable")
    security = ctypes.CDLL(security_path)
    core = ctypes.CDLL(core_path)
    security.SecKeychainOpen.argtypes = [ctypes.c_char_p, ctypes.POINTER(_Void)]
    security.SecKeychainOpen.restype = ctypes.c_int32
    security.SecKeychainAddGenericPassword.argtypes = [
        _Void, _UInt, ctypes.c_char_p, _UInt, ctypes.c_char_p, _UInt, _Void,
        ctypes.POINTER(_Void)]
    security.SecKeychainAddGenericPassword.restype = ctypes.c_int32
    security.SecKeychainFindGenericPassword.argtypes = [
        _Void, _UInt, ctypes.c_char_p, _UInt, ctypes.c_char_p,
        ctypes.POINTER(_UInt), ctypes.POINTER(_Void), ctypes.POINTER(_Void)]
    security.SecKeychainFindGenericPassword.restype = ctypes.c_int32
    security.SecKeychainItemModifyContent.argtypes = [_Void, _Void, _UInt, _Void]
    security.SecKeychainItemModifyContent.restype = ctypes.c_int32
    security.SecKeychainItemFreeContent.argtypes = [_Void, _Void]
    security.SecKeychainItemFreeContent.restype = ctypes.c_int32
    core.CFRelease.argtypes = [_Void]
    return security, core


def _keychain_ref(security, path: Optional[Path]):
    if path is None:
        return _Void()
    reference = _Void()
    status = security.SecKeychainOpen(str(path).encode("utf-8"), ctypes.byref(reference))
    if status:
        raise OSError("keychain_open_failed")
    return reference


def set_password(service: str, account: str, password: str,
                 *, keychain_path: Optional[Path] = None) -> None:
    if not all(isinstance(item, str) and item for item in (service, account, password)):
        raise ValueError("invalid_keychain_item")
    security, core = _frameworks()
    keychain = _keychain_ref(security, keychain_path)
    service_bytes, account_bytes, password_bytes = (
        service.encode("utf-8"), account.encode("utf-8"), password.encode("utf-8"))
    item = _Void()
    try:
        status = security.SecKeychainFindGenericPassword(
            keychain, len(service_bytes), service_bytes, len(account_bytes), account_bytes,
            None, None, ctypes.byref(item))
        if status == 0:
            status = security.SecKeychainItemModifyContent(
                item, None, len(password_bytes), ctypes.c_char_p(password_bytes))
        elif status == -25300:  # errSecItemNotFound
            status = security.SecKeychainAddGenericPassword(
                keychain, len(service_bytes), service_bytes, len(account_bytes), account_bytes,
                len(password_bytes), ctypes.c_char_p(password_bytes), None)
        if status:
            raise OSError("keychain_write_failed")
    finally:
        if item.value:
            core.CFRelease(item)
        if keychain.value:
            core.CFRelease(keychain)


def get_password(service: str, account: str,
                 *, keychain_path: Optional[Path] = None) -> Optional[str]:
    if not all(isinstance(item, str) and item for item in (service, account)):
        raise ValueError("invalid_keychain_item")
    security, core = _frameworks()
    keychain = _keychain_ref(security, keychain_path)
    service_bytes, account_bytes = service.encode("utf-8"), account.encode("utf-8")
    length = _UInt()
    data = _Void()
    try:
        status = security.SecKeychainFindGenericPassword(
            keychain, len(service_bytes), service_bytes, len(account_bytes), account_bytes,
            ctypes.byref(length), ctypes.byref(data), None)
        if status == -25300:
            return None
        if status:
            raise OSError("keychain_read_failed")
        return ctypes.string_at(data, length.value).decode("utf-8")
    finally:
        if data.value:
            security.SecKeychainItemFreeContent(None, data)
        if keychain.value:
            core.CFRelease(keychain)
