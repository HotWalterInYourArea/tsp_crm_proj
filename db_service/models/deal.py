from db_service.models.abstract_models.item import Item
from sqlalchemy import(
String, Integer, ForeignKey)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid
from sqlalchemy.dialects.postgresql import UUID as PgUUID

class Deal(Item):
    __tablename__ = 'deal'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новая сделка")
    main_client: Mapped["Client"] = relationship('Client', back_populates = 'deal_ids')
    main_client_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('client.id'), nullable = False)
    contact_clients: Mapped[list["Client"]] = relationship('Client', back_populates = 'deal_ids', secondary = 'contact_client_deal')
    assigned_by: Mapped["User"] = relationship("User", back_populates = "assigned_deals")
    created_by: Mapped["User"] = relationship("User", back_populates = "created_deals")
    assigned_by_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('user.id'), nullable = False)
    created_by_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('user.id'), nullable = False)
    supervised_by:  Mapped[list["User"]] = relationship("User", back_populates = "supervised_deals", secondary = 'supervisor_user_deal')
    budget: Mapped[int] = mapped_column(Integer, nullable = True)
    activities: Mapped[list["Activity"]] = relationship('Activity', back_populates = 'deal_id', cascade = 'all,delete')