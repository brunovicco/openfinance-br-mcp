"""Contains all the data models used in inputs/outputs"""

from clients.consents_v3_3_1.models.business_entity import BusinessEntity
from clients.consents_v3_3_1.models.business_entity_document import BusinessEntityDocument
from clients.consents_v3_3_1.models.business_entity_document_extensions import BusinessEntityDocumentExtensions
from clients.consents_v3_3_1.models.business_entity_extensions import BusinessEntityExtensions
from clients.consents_v3_3_1.models.consents_delete_consents_consent_id_response_529 import (
    ConsentsDeleteConsentsConsentIdResponse529,
)
from clients.consents_v3_3_1.models.consents_delete_consents_consent_id_response_529_errors_item import (
    ConsentsDeleteConsentsConsentIdResponse529ErrorsItem,
)
from clients.consents_v3_3_1.models.consents_delete_consents_consent_id_response_529_meta import (
    ConsentsDeleteConsentsConsentIdResponse529Meta,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529 import (
    ConsentsGetConsentsConsentIdExtensionsResponse529,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_errors_item import (
    ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_extensions_response_529_meta import (
    ConsentsGetConsentsConsentIdExtensionsResponse529Meta,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_response_529 import (
    ConsentsGetConsentsConsentIdResponse529,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_response_529_errors_item import (
    ConsentsGetConsentsConsentIdResponse529ErrorsItem,
)
from clients.consents_v3_3_1.models.consents_get_consents_consent_id_response_529_meta import (
    ConsentsGetConsentsConsentIdResponse529Meta,
)
from clients.consents_v3_3_1.models.consents_post_consents_consent_id_extends_response_529 import (
    ConsentsPostConsentsConsentIdExtendsResponse529,
)
from clients.consents_v3_3_1.models.consents_post_consents_consent_id_extends_response_529_errors_item import (
    ConsentsPostConsentsConsentIdExtendsResponse529ErrorsItem,
)
from clients.consents_v3_3_1.models.consents_post_consents_consent_id_extends_response_529_meta import (
    ConsentsPostConsentsConsentIdExtendsResponse529Meta,
)
from clients.consents_v3_3_1.models.consents_post_consents_response_529 import ConsentsPostConsentsResponse529
from clients.consents_v3_3_1.models.consents_post_consents_response_529_errors_item import (
    ConsentsPostConsentsResponse529ErrorsItem,
)
from clients.consents_v3_3_1.models.consents_post_consents_response_529_meta import (
    ConsentsPostConsentsResponse529Meta,
)
from clients.consents_v3_3_1.models.create_consent import CreateConsent
from clients.consents_v3_3_1.models.create_consent_data import CreateConsentData
from clients.consents_v3_3_1.models.create_consent_data_permissions_item import CreateConsentDataPermissionsItem
from clients.consents_v3_3_1.models.create_consent_extensions import CreateConsentExtensions
from clients.consents_v3_3_1.models.create_consent_extensions_data import CreateConsentExtensionsData
from clients.consents_v3_3_1.models.enum_rejected_by import EnumRejectedBy
from clients.consents_v3_3_1.models.field_422_response_error_create_consent import Field422ResponseErrorCreateConsent
from clients.consents_v3_3_1.models.field_422_response_error_create_consent_errors_item import (
    Field422ResponseErrorCreateConsentErrorsItem,
)
from clients.consents_v3_3_1.models.field_422_response_error_create_consent_errors_item_code import (
    Field422ResponseErrorCreateConsentErrorsItemCode,
)
from clients.consents_v3_3_1.models.links import Links
from clients.consents_v3_3_1.models.links_consents import LinksConsents
from clients.consents_v3_3_1.models.logged_user import LoggedUser
from clients.consents_v3_3_1.models.logged_user_document import LoggedUserDocument
from clients.consents_v3_3_1.models.logged_user_document_extensions import LoggedUserDocumentExtensions
from clients.consents_v3_3_1.models.logged_user_extensions import LoggedUserExtensions
from clients.consents_v3_3_1.models.meta import Meta
from clients.consents_v3_3_1.models.meta_error import MetaError
from clients.consents_v3_3_1.models.meta_extensions import MetaExtensions
from clients.consents_v3_3_1.models.response_consent import ResponseConsent
from clients.consents_v3_3_1.models.response_consent_data import ResponseConsentData
from clients.consents_v3_3_1.models.response_consent_data_permissions_item import ResponseConsentDataPermissionsItem
from clients.consents_v3_3_1.models.response_consent_data_status import ResponseConsentDataStatus
from clients.consents_v3_3_1.models.response_consent_extensions import ResponseConsentExtensions
from clients.consents_v3_3_1.models.response_consent_extensions_data import ResponseConsentExtensionsData
from clients.consents_v3_3_1.models.response_consent_extensions_data_permissions_item import (
    ResponseConsentExtensionsDataPermissionsItem,
)
from clients.consents_v3_3_1.models.response_consent_extensions_data_status import ResponseConsentExtensionsDataStatus
from clients.consents_v3_3_1.models.response_consent_read import ResponseConsentRead
from clients.consents_v3_3_1.models.response_consent_read_data import ResponseConsentReadData
from clients.consents_v3_3_1.models.response_consent_read_data_journey import ResponseConsentReadDataJourney
from clients.consents_v3_3_1.models.response_consent_read_data_permissions_item import (
    ResponseConsentReadDataPermissionsItem,
)
from clients.consents_v3_3_1.models.response_consent_read_data_rejection import ResponseConsentReadDataRejection
from clients.consents_v3_3_1.models.response_consent_read_data_rejection_reason import (
    ResponseConsentReadDataRejectionReason,
)
from clients.consents_v3_3_1.models.response_consent_read_data_rejection_reason_code import (
    ResponseConsentReadDataRejectionReasonCode,
)
from clients.consents_v3_3_1.models.response_consent_read_data_status import ResponseConsentReadDataStatus
from clients.consents_v3_3_1.models.response_consent_read_extensions import ResponseConsentReadExtensions
from clients.consents_v3_3_1.models.response_consent_read_extensions_data_item import (
    ResponseConsentReadExtensionsDataItem,
)
from clients.consents_v3_3_1.models.response_error import ResponseError
from clients.consents_v3_3_1.models.response_error_errors_item import ResponseErrorErrorsItem
from clients.consents_v3_3_1.models.response_error_unprocessable_entity import ResponseErrorUnprocessableEntity
from clients.consents_v3_3_1.models.response_error_unprocessable_entity_delete import (
    ResponseErrorUnprocessableEntityDelete,
)
from clients.consents_v3_3_1.models.response_error_unprocessable_entity_delete_errors_item import (
    ResponseErrorUnprocessableEntityDeleteErrorsItem,
)
from clients.consents_v3_3_1.models.response_error_unprocessable_entity_delete_errors_item_code import (
    ResponseErrorUnprocessableEntityDeleteErrorsItemCode,
)
from clients.consents_v3_3_1.models.response_error_unprocessable_entity_errors_item import (
    ResponseErrorUnprocessableEntityErrorsItem,
)
from clients.consents_v3_3_1.models.response_error_unprocessable_entity_errors_item_code import (
    ResponseErrorUnprocessableEntityErrorsItemCode,
)

__all__ = (
    "BusinessEntity",
    "BusinessEntityDocument",
    "BusinessEntityDocumentExtensions",
    "BusinessEntityExtensions",
    "ConsentsDeleteConsentsConsentIdResponse529",
    "ConsentsDeleteConsentsConsentIdResponse529ErrorsItem",
    "ConsentsDeleteConsentsConsentIdResponse529Meta",
    "ConsentsGetConsentsConsentIdExtensionsResponse529",
    "ConsentsGetConsentsConsentIdExtensionsResponse529ErrorsItem",
    "ConsentsGetConsentsConsentIdExtensionsResponse529Meta",
    "ConsentsGetConsentsConsentIdResponse529",
    "ConsentsGetConsentsConsentIdResponse529ErrorsItem",
    "ConsentsGetConsentsConsentIdResponse529Meta",
    "ConsentsPostConsentsConsentIdExtendsResponse529",
    "ConsentsPostConsentsConsentIdExtendsResponse529ErrorsItem",
    "ConsentsPostConsentsConsentIdExtendsResponse529Meta",
    "ConsentsPostConsentsResponse529",
    "ConsentsPostConsentsResponse529ErrorsItem",
    "ConsentsPostConsentsResponse529Meta",
    "CreateConsent",
    "CreateConsentData",
    "CreateConsentDataPermissionsItem",
    "CreateConsentExtensions",
    "CreateConsentExtensionsData",
    "EnumRejectedBy",
    "Field422ResponseErrorCreateConsent",
    "Field422ResponseErrorCreateConsentErrorsItem",
    "Field422ResponseErrorCreateConsentErrorsItemCode",
    "Links",
    "LinksConsents",
    "LoggedUser",
    "LoggedUserDocument",
    "LoggedUserDocumentExtensions",
    "LoggedUserExtensions",
    "Meta",
    "MetaError",
    "MetaExtensions",
    "ResponseConsent",
    "ResponseConsentData",
    "ResponseConsentDataPermissionsItem",
    "ResponseConsentDataStatus",
    "ResponseConsentExtensions",
    "ResponseConsentExtensionsData",
    "ResponseConsentExtensionsDataPermissionsItem",
    "ResponseConsentExtensionsDataStatus",
    "ResponseConsentRead",
    "ResponseConsentReadData",
    "ResponseConsentReadDataJourney",
    "ResponseConsentReadDataPermissionsItem",
    "ResponseConsentReadDataRejection",
    "ResponseConsentReadDataRejectionReason",
    "ResponseConsentReadDataRejectionReasonCode",
    "ResponseConsentReadDataStatus",
    "ResponseConsentReadExtensions",
    "ResponseConsentReadExtensionsDataItem",
    "ResponseError",
    "ResponseErrorErrorsItem",
    "ResponseErrorUnprocessableEntity",
    "ResponseErrorUnprocessableEntityDelete",
    "ResponseErrorUnprocessableEntityDeleteErrorsItem",
    "ResponseErrorUnprocessableEntityDeleteErrorsItemCode",
    "ResponseErrorUnprocessableEntityErrorsItem",
    "ResponseErrorUnprocessableEntityErrorsItemCode",
)
