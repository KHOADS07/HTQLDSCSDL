"""Khởi tạo CSDL SQLite và cung cấp kết nối dùng chung."""

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().with_name("thuvien.db")

SCHEMA = """
BEGIN;
CREATE TABLE IF NOT EXISTS DocGia (
    MaDocGia INTEGER PRIMARY KEY,
    HoTen TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS Sach (
    MaSach INTEGER PRIMARY KEY,
    TenSach TEXT NOT NULL,
    TacGia TEXT NOT NULL,
    SoLuongTong INTEGER NOT NULL CHECK (SoLuongTong >= 0),
    SoLuongCon INTEGER NOT NULL CHECK (SoLuongCon BETWEEN 0 AND SoLuongTong)
);
CREATE TABLE IF NOT EXISTS PhieuMuon (
    MaPhieuMuon INTEGER PRIMARY KEY,
    MaDocGia INTEGER NOT NULL REFERENCES DocGia(MaDocGia),
    MaSach INTEGER NOT NULL REFERENCES Sach(MaSach),
    NgayMuon TEXT NOT NULL,
    HanTra TEXT NOT NULL CHECK (HanTra >= NgayMuon),
    NgayTraThucTe TEXT CHECK (NgayTraThucTe >= NgayMuon),
    TienPhat INTEGER NOT NULL DEFAULT 0 CHECK (TienPhat >= 0),
    DaDongPhat INTEGER NOT NULL DEFAULT 0 CHECK (DaDongPhat IN (0, 1))
);
COMMIT;
"""


def get_connection(db_path=DB_PATH):
    """Mở kết nối có kiểm tra khóa ngoại. Bên gọi chịu trách nhiệm đóng."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=DB_PATH):
    with closing(get_connection(db_path)) as conn:
        conn.executescript(SCHEMA)


if __name__ == "__main__":
    init_db()
    print(f"Đã khởi tạo CSDL: {DB_PATH}")
