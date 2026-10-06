from db_service.models.abstract_models.item import Base
from sqlalchemy import Table, Column, ForeignKey

supervisor_user_deal = Table(
    'supervisor_user_deal',
    Base.metadata,
    Column(
        'supervisor_user_id',
        ForeignKey('user.id'),
        primary_key=True
    ),
    Column(
            'supervised_deal_id',
            ForeignKey('deal.id'),
            primary_key=True
        )               
)
contact_client_deal = Table(
    'contact_client_deal',
    Base.metadata,
    Column(
        'contact_client_id',
        ForeignKey('client.id'),
        primary_key=True
    ),
    Column(
            'deal_id',
            ForeignKey('deal.id'),
            primary_key=True
        )               
)