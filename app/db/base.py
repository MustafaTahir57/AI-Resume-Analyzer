# app/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# DeclarativeBase ek built-in class hai jo humein us "machinery" (metadata tracking + mapping logic + table-creation methods) ko free mein deti hai — hum khud se registry ya conversion logic likhne ki zehmat nahi karte, bas is class ko inherit karke apna Base bana lete hain, aur uske baad har model us Base se inherit karega taake wo automatically is system ka hissa ban jaye.