import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.transaction import atomic
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView

from core.api_permissions import CanView, CanAdd, CanChange, CanDelete
from core.const import DATA, ERROR_TYPE, ERRORS, MESSAGE, VALIDATION_ERROR, HTTP_404, INTEGRITY_ERROR, INVALID_DATA, \
    OTHER
from core.exceptions import InvalidData, APIException202
from core.serializers import ResponseWithResultSerializer, ResponseSerializer
from core.utils import success_response, error_response

from typing import Any, Mapping, Optional
from django.http import HttpRequest
from core.signals import audit_event


logger = logging.getLogger(__name__)


@permission_classes([CanView])
class BaseListAPIView(ListAPIView):
    queryset = None
    serializer_class = None
    filter_serializer_class = None
    filter_map = {}
    queryset_kwargs = {}

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(ResponseWithResultSerializer.success(serializer.data))

            serializer = self.get_serializer(queryset, many=True)
            try:
                model = getattr(self.get_queryset(), "model", None)
                target_type = f"{model._meta.app_label}.{model._meta.model_name}" if model else "Unknown"
                total = getattr(queryset, "count", lambda: None)()
                audit_event.send(
                    sender=self.__class__,
                    actor=getattr(request, "user", None),
                    action="READ",
                    target_type=target_type,
                    target_id="",  # list has no single target
                    ip_address=_client_ip(request),
                    metadata={"count": total} if total is not None else {},
                )
            except Exception:
                pass
            return success_response(result=serializer.data)
        except Exception as e:
            return error_response(message="Failed to fetch list", status=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[str(e)])


@permission_classes([CanView])
class BaseRetrieveAPIView(RetrieveAPIView):
    queryset = None
    serializer_class = None
    filter_serializer_class = None
    filter_map = {}
    queryset_kwargs = {}

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            try:
                target_type, target_id = _target_from_instance(instance)
                audit_event.send(
                    sender=self.__class__,
                    actor=getattr(request, "user", None),
                    action="READ",
                    target_type=target_type,
                    target_id=target_id,
                    ip_address=_client_ip(request),
                    metadata={},
                )
            except Exception:
                pass
            return success_response(result=serializer.data)
        except Http404 as e:
            return error_response(
                message="Object not found",
                errors=[str(e)],
                status=status.HTTP_404_NOT_FOUND,
                error_type=OTHER
            )
        except Exception as e:
            return error_response(
                message="Failed to fetch object",
                errors=[str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=OTHER
            )

class BaseCreateAPIView(CreateAPIView):

    @atomic
    @permission_classes([CanAdd])
    def create(self, request, *args, **kwargs):
        data = {}

        if 'data' in request.data:  # POST request with FILES
            for key in request.FILES.keys():
                data[key] = request.FILES[key]
            post_data = json.loads(request.data['data'])
            data.update(post_data)
        else:  # SIMPLE POST request
            data = request.data.copy()
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            try:
                instance = getattr(serializer, "instance", None)
                if instance is not None:
                    target_type, target_id = _target_from_instance(instance)
                    audit_event.send(
                        sender=self.__class__,
                        actor=getattr(request, "user", None),
                        action="CREATE",
                        target_type=target_type,
                        target_id=target_id,
                        ip_address=_client_ip(request),
                        metadata={},
                    )
            except Exception:
                pass

            # headers = self.get_success_headers(serializer.data)
            return success_response(result=serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            error_dict = ve.get_full_details()
            return error_response(
                message=get_validation_error_message(error_dict),
                errors=[str(err) for err in error_dict.values()],
                error_type=VALIDATION_ERROR,
            )
        except ObjectDoesNotExist as dne:
            return error_response(
                message="Object does not exist",
                errors=[str(dne)],
                status=status.HTTP_404_NOT_FOUND,
                error_type=HTTP_404
            )
        except IntegrityError as ie:
            return error_response(
                message="Object already exists",
                errors=[str(ie)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=INTEGRITY_ERROR
            )
        except InvalidData as ex:
            return error_response(
                message=str(ex.get_message()),
                error_type=INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST
            )
        except APIException202 as ae:
            # headers = self.get_success_headers(serializer.data)
            return success_response(result=ae.obj, message=ae.message)
        except Exception as e:
            return error_response(
                message="Internal server error",
                errors=[str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=OTHER
            )


class BaseLCAPIView(BaseCreateAPIView, BaseListAPIView):
    list_read_serializer_class = None
    read_serializer_class = None
    write_serializer_class = None
    filter_serializer_class = None
    serializer_error_msg = "'%s' should either include a `serializer_class` attribute, or override the " \
                           "`get_serializer_class()` method."
    queryset = None
    filter_map = {}

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.list_read_serializer_class is not None:
                return self.list_read_serializer_class
            assert self.read_serializer_class is not None or self.serializer_class is not None, (
                    self.serializer_error_msg % self.__class__.__name__)
            return self.read_serializer_class
        if self.request.method == 'POST':
            assert self.write_serializer_class is not None or self.serializer_class is not None, (
                    self.serializer_error_msg % self.__class__.__name__)
            return self.write_serializer_class
        assert self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
        return self.serializer_class


class BaseRUDAPIView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an object instance with standardized responses.
    """
    queryset = None
    serializer_class = None
    read_serializer_class = None
    write_serializer_class = None
    serializer_error_msg = "'%s' should either include a `serializer_class` attribute, or override the `get_serializer_class()` method."
    delete_obj_id_physical = None

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.read_serializer_class or self.serializer_class
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return self.write_serializer_class or self.serializer_class
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(result=serializer.data)
        except Http404 as e:
            return error_response(
                message="Object not found",
                errors=[str(e)],
                status=status.HTTP_404_NOT_FOUND,
                error_type=HTTP_404
            )
        except Exception as e:
            return error_response(
                message="Internal server error",
                errors=[str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=OTHER
            )

    @atomic
    @permission_classes([CanChange])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {}

        # handle file uploads + json data
        if 'data' in request.data:
            for key in request.FILES.keys():
                data[key] = request.FILES[key]
            post_data = json.loads(request.data['data'])
            data.update(post_data)
        else:
            data = request.data.copy()

        serializer = self.get_serializer(instance, data=data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            try:
                instance = getattr(serializer, "instance", None)
                if instance is not None:
                    target_type, target_id = _target_from_instance(instance)
                    audit_event.send(
                        sender=self.__class__,
                        actor=getattr(request, "user", None),
                        action="UPDATE",
                        target_type=target_type,
                        target_id=target_id,
                        ip_address=_client_ip(request),
                        metadata={},
                    )
            except Exception:
                pass
            return success_response(result=serializer.data)
        except ValidationError as ve:
            error_dict = ve.get_full_details()
            return error_response(
                message="Validation error",
                errors=error_dict,
                status=status.HTTP_400_BAD_REQUEST,
                error_type=VALIDATION_ERROR
            )
        except IntegrityError as ie:
            return error_response(
                message="Integrity error",
                errors=[str(ie)],
                status=status.HTTP_400_BAD_REQUEST,
                error_type=INTEGRITY_ERROR
            )
        except Exception as e:
            return error_response(
                message="Failed to update object",
                errors=[str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=OTHER
            )

    @permission_classes([CanDelete])
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            target_type, target_id = _target_from_instance(instance)

            self.perform_destroy(instance)

            try:
                audit_event.send(
                    sender=self.__class__,
                    actor=getattr(request, "user", None),
                    action="DELETE",
                    target_type=target_type,
                    target_id=target_id,
                    ip_address=_client_ip(request),
                    metadata={},
                )
            except Exception:
                pass

            return success_response(message="Deleted object", status=status.HTTP_204_NO_CONTENT)

        except Http404 as e:
            return error_response(
                message="Object not found",
                errors=[str(e)],
                status=status.HTTP_404_NOT_FOUND,
                error_type=HTTP_404,
            )
        except IntegrityError as ie:
            return error_response(
                message="Integrity error",
                errors=[str(ie)],
                status=status.HTTP_400_BAD_REQUEST,
                error_type=INTEGRITY_ERROR,
            )
        except Exception as e:
            return error_response(
                message="Failed to delete object",
                errors=[str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type=OTHER,
            )


def get_validation_error_message(error_data):
    try:
        response_message = ''
        if isinstance(error_data, dict):
            for key, value in error_data.items():
                for item in value:
                    if 'message' in item:
                        response_message += '{}: {} '.format(key, item['message'])
                    else:
                        if isinstance(item, dict):
                            for unit_key, unit_value in item.items():
                                for arr_item in unit_value:
                                    response_message += '{}: {} '.format(unit_key, arr_item['message'])
                        elif isinstance(item, str):
                            for item_key, item_val in value.items():
                                for arr_item in item_val:
                                    response_message += '{}: {} '.format(item_key, arr_item['message'])
        elif isinstance(error_data, list):
            for arr_item in error_data:
                response_message += '{} '.format(arr_item['message'])
    except:
        response_message = 'Error {}'.format(error_data)
    return response_message



def _client_ip(request: HttpRequest) -> Optional[str]:
    try:
        xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
    except Exception:
        return None

def _target_from_instance(instance: Any) -> tuple[str, str]:
    try:
        meta = instance._meta  # type: ignore[attr-defined]
        target_type = f"{meta.app_label}.{meta.model_name}"
        target_id = str(getattr(instance, "pk", "") or getattr(instance, "id", ""))
        return target_type, target_id
    except Exception:
        return ("Unknown", "")