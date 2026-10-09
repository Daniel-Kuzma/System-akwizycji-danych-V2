from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, Enum, func
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    public_id : Mapped[uuid.UUID] = mapped_column(default = uuid.uuid4, unique = True)
    name : Mapped[str] = mapped_column()
    lastname : Mapped[str] = mapped_column()
    username : Mapped[str] = mapped_column(unique = True)
    password : Mapped[str] = mapped_column()
    email : Mapped[str] = mapped_column(unique = True)
    is_active : Mapped[bool] = mapped_column(default = True)
    user_role : Mapped[str] = mapped_column(Enum("user", "admin", name = "enum_name"), default = "user")
    created_at : Mapped[datetime] = mapped_column(server_default = func.now())

class TypyOfCultivation(Base):
    __tablename__ = "types_of_cultivations"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    name_of_cultivation : Mapped[str] = mapped_column()
    min_temperature : Mapped[float] = mapped_column()
    max_temperature : Mapped[float] = mapped_column()
    min_humidity : Mapped[float] = mapped_column()
    max_humidity : Mapped[float] = mapped_column()

class Device(Base):
    __tablename__ = "devices"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    owner_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    type_of_cultivation_id : Mapped[int] = mapped_column(ForeignKey("types_of_cultivations.id"))
    secret_device_token : Mapped[str] = mapped_column()
    device_name : Mapped[str] = mapped_column()
    device_location : Mapped[str] = mapped_column()

class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    device_id : Mapped[int] = mapped_column(ForeignKey("devices.id"))
    temperature_reading : Mapped[float] = mapped_column()
    humidity_reading : Mapped[float] = mapped_column()
    date_reading : Mapped[datetime] = mapped_column(server_default = func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    action : Mapped[str] = mapped_column(Enum("CREATE", "UPDATE", "DELETE", name = "cud_enum"))
    entity_type : Mapped[str] = mapped_column() # user, device, device_api_key, type_of_cultivation
    entity_id : Mapped[int] = mapped_column() 
    created_at : Mapped[datetime] = mapped_column(server_default = func.now())

class DeviceApiKey(Base):
    __tablename__ = "device_api_keys"
    id : Mapped[int] = mapped_column(primary_key = True, index = True)
    device_id : Mapped[int] = mapped_column(ForeignKey("devices.id"))
    token : Mapped[str] = mapped_column(unique = True)
    is_active : Mapped[bool] = mapped_column(default = True)
    created_at : Mapped[datetime] = mapped_column(server_default = func.now())