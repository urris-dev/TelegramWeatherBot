from sqlalchemy import ForeignKey
from sqlalchemy import Integer, VARCHAR, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"

    name = mapped_column(VARCHAR(30), primary_key=True)
    subscribed_user_ids = mapped_column(MutableList.as_mutable(
        ARRAY(BigInteger)), server_default="{}", nullable=False)

    def __repr__(self):
        return f"City(name={self.name!r})"


class Weather(Base):
    __tablename__ = "weather"
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    city = mapped_column(ForeignKey("cities.name"), nullable=False)
    forecast_date = mapped_column(VARCHAR(10), nullable=False)
    timestamp = mapped_column(BigInteger, server_default='0', nullable=False)
    weather = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"Weather(city={self.city!r}, forecast_date={self.forecast_date!r})"
