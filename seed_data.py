"""Tạo dữ liệu mẫu theo MSSV vào CSDL trống."""

import argparse
import random
from contextlib import closing
from datetime import date, timedelta

from database import DB_PATH, get_connection, init_db

READERS = ("Nguyễn An", "Trần Bình", "Lê Chi", "Phạm Dũng", "Võ Hà", "Đỗ Hạnh")
BOOKS = (
    ("Dế Mèn phiêu lưu ký", "Tô Hoài"),
    ("Đất rừng phương Nam", "Đoàn Giỏi"),
    ("Quê nội", "Võ Quảng"),
    ("Lá cờ thêu sáu chữ vàng", "Nguyễn Huy Tưởng"),
    ("Tôi thấy hoa vàng trên cỏ xanh", "Nguyễn Nhật Ánh"),
    ("Vừa nhắm mắt vừa mở cửa sổ", "Nguyễn Ngọc Thuần"),
)


def seed_database(mssv, db_path=DB_PATH, as_of=None):
    if not mssv.strip():
        raise ValueError("MSSV không được để trống.")

    rng = random.Random(mssv.strip())
    today = as_of or date.today()
    readers = [
        (reader_id, name, f"docgia{reader_id}@example.test")
        for reader_id, name in enumerate(rng.sample(READERS, len(READERS)), 1)
    ]
    books = []
    loans = []
    reader_ids = rng.sample(range(1, len(readers) + 1), len(BOOKS))
    for book_id, (title, author) in enumerate(rng.sample(BOOKS, len(BOOKS)), 1):
        total = 1 if book_id == 1 else rng.randint(2, 6)
        books.append((book_id, title, author, total, total - 1))
        reader_id = reader_ids[book_id - 1]

        # Sách đầu tiên hết tồn và có một phiếu đang quá hạn.
        borrowed = today - timedelta(days=21 if book_id == 1 else rng.randint(1, 10))
        due = borrowed + timedelta(days=14)
        loans.append((reader_id, book_id, borrowed.isoformat(), due.isoformat(), None, 0))

        # Phiếu cũ của sách đầu tiên trả trễ và còn nợ khoản phạt mẫu.
        borrowed = today - timedelta(days=rng.randint(30, 60))
        due = borrowed + timedelta(days=14)
        returned = due + timedelta(days=2) if book_id == 1 else due
        fine = 10000 if book_id == 1 else 0
        loans.append(
            (reader_id, book_id, borrowed.isoformat(), due.isoformat(), returned.isoformat(), fine)
        )

    init_db(db_path)
    with closing(get_connection(db_path)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        occupied = conn.execute(
            "SELECT EXISTS (SELECT 1 FROM DocGia) OR EXISTS (SELECT 1 FROM Sach) "
            "OR EXISTS (SELECT 1 FROM PhieuMuon)"
        ).fetchone()[0]
        if occupied:
            raise ValueError("CSDL đã có dữ liệu. Hãy chọn file mẫu mới bằng --db.")
        conn.executemany(
            "INSERT INTO DocGia (MaDocGia, HoTen, Email) VALUES (?, ?, ?)", readers
        )
        conn.executemany(
            "INSERT INTO Sach (MaSach, TenSach, TacGia, SoLuongTong, SoLuongCon) "
            "VALUES (?, ?, ?, ?, ?)",
            books,
        )
        conn.executemany(
            "INSERT INTO PhieuMuon (MaDocGia, MaSach, NgayMuon, HanTra, NgayTraThucTe, TienPhat) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            loans,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo dữ liệu SQLite mẫu theo MSSV.")
    parser.add_argument("mssv")
    parser.add_argument("--db", default=DB_PATH, help="Đường dẫn file SQLite")
    parser.add_argument("--as-of", type=date.fromisoformat, help="Ngày tham chiếu YYYY-MM-DD")
    args = parser.parse_args()
    try:
        seed_database(args.mssv, args.db, args.as_of)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Đã tạo dữ liệu mẫu: {args.db}")
