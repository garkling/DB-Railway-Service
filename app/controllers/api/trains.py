from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_train_service
from app.dto.responses import RescheduleTrainResponse, TrainResponse
from app.dto.train_dto import RescheduleTrainDTO
from app.services.commands import RescheduleTrainCommand
from app.services.train_service import TrainService

router = APIRouter()


@router.put(
    "/{train_number}/{service_date}",
    response_model=RescheduleTrainResponse,
)
def reschedule_train_api(
    train_number: str,
    service_date: date,
    dto: RescheduleTrainDTO,
    svc: TrainService = Depends(get_train_service),
) -> RescheduleTrainResponse:
    cmd = RescheduleTrainCommand.from_dto(
        dto, current_train_number=train_number, current_service_date=service_date,
    )
    result = svc.reschedule_train(cmd)
    return RescheduleTrainResponse(
        train=TrainResponse.from_domain(result.updated_train),
        coaches_cascaded=len(result.after.coaches),
        tickets_cascaded=len(result.after.tickets),
    )
