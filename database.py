import sqlite3
from tkinter import W
import random
from functools import wraps
from unittest import result

def with_db_collection(func: callable) -> callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        try:
            result = func(cur, *args, **kwargs)
            con.commit()
        except Exception as e:
            con.rollback()
            print(f"ОШИБКА: {e}")
        finally:
            con.close()
        return result
    return wrapper


def create_tables() -> None:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INTEGER,
        username TEXT,
        role TEXT,
        mafia_vote INTEGER,
        citizen_vote INTEGER,
        voted INTEGER, 
        dead INTEGER)
    """)
    con.commit()
    con.close()

def insert_player(player_id:int, username:str,) -> None:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"INSERT INTO players(player_id, username, mafia_vote, citizen_vote, voted, dead)\
        VALUES (?, ?, ?, ?, ?, ?)"
    cur.execute(sql, (player_id, username, 0, 0, 0, 0))
    con.commit()
    con.close()

def players_amount() -> int:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_mafia_us() -> str:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    data = cur.fetchall()
    names = ""
    for row in data:
        name = row[0]
        names += name + "\n"
    con.close()
    return names

def get_pl_roles() -> list:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data

def get_all_alive() -> list:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = "SELECT username  FROM players WHERE dead=0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data

def set_roles(players: int) -> None:
    game_roles = ["citizen"] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = "mafia"
    random.shuffle(game_roles)
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT player_id FROM players")
    players_id = cur.fetchall()
    for role, player_id in zip(game_roles, players_id):
        sql = "UPDATE players SET role=? WHERE player_id=?"
        cur.execute(sql, (role, player_id[0]))
    con.commit()
    con.close()

from typing import Callable, Literal

def vote(type: str, username: str, player_id: int) -> bool:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE player_id=? AND dead=0 AND voted=0", (player_id,))
    can_vote = cur.fetchone()
    if can_vote:
        cur.execute(f"UPDATE players SET {type} = {type} + 1 WHERE username=?", (username,))
        cur.execute(f"UPDATE players SET voted=1 WHERE player_id=?", (player_id,))
        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill() -> str:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE mafia_vote=?", (max_votes,))
    mafia_alive = cur.fetchone()[0]
    username_killed = "никого"
    if max_votes == mafia_alive:
        cur.execute("SELECT username FROM players WHERE mafia_vote=?", (max_votes,))
        username_killed = cur.fetchone()
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        con.commit()
    con.close
    return username_killed

def citizen_kill() -> str:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE citizen_vote=?", (max_votes,))
    max_count = cur.fetchone()[0]
    username_killed = "никого"
    if max_count ==1:
        cur.execute("SELECT username FROM players WHERE citizen_vote=?", (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        con.commit()
    con.close
    return username_killed

@with_db_collection
def check_winner(cur) -> str | None:
    cur.execute("SELECT COUNT(*) FROM players WHERE role='mafia' and dead=0")
    mafia_alive = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE role!='mafia' and dead=0")
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return "Мафия"
    elif mafia_alive == 0:
        return "Горожане"
    return None

@with_db_collection
def clear(cur, dead: bool=False) -> None:
    sql = "UPDATE players SET citizen_vote=0, mafia_vote=0, voted=0"
    if dead:
        sql += ", dead=0"
    cur.execute(sql)

if __name__ == "__main__":
#    create_tables()
#    insert_player(1, "гиде")
#    print(players_amount())
#    print(get_mafia_us())
#    print(get_pl_roles())
#    print(get_all_alive())
#    print(set_roles(players_amount()))
#    print(vote("mafia_vote", "Ры", "1"))
    print(check_winner())
    print(clear())

