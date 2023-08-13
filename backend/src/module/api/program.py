import logging
import os
import signal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from module.core import Program
from module.conf import VERSION
from module.security.api import get_current_user, UNAUTHORIZED

logger = logging.getLogger(__name__)
program = Program()
router = APIRouter(tags=["program"])


@router.on_event("startup")
async def startup():
    program.startup()


@router.on_event("shutdown")
async def shutdown():
    program.stop()


@router.get("/restart")
async def restart(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    try:
        program.restart()
        return {"status": "ok"}
    except Exception as e:
        logger.debug(e)
        logger.warning("Failed to restart program")
        raise HTTPException(status_code=500, detail="Failed to restart program")


@router.get("/start")
async def start(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    try:
        return program.start()
    except Exception as e:
        logger.debug(e)
        logger.warning("Failed to start program")
        raise HTTPException(status_code=500, detail="Failed to start program")


@router.get("/stop")
async def stop(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    return program.stop()


@router.get("/status")
async def program_status(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    if not program.is_running:
        return {
            "status": False,
            "version": VERSION,
        }
    else:
        return {
            "status": True,
            "version": VERSION,
        }


@router.get("/shutdown")
async def shutdown_program(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    program.stop()
    logger.info("Shutting down program...")
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "ok"}


# Check status
@router.get("/check/downloader", tags=["check"])
async def check_downloader_status(current_user=Depends(get_current_user)):
    if not current_user:
        raise UNAUTHORIZED
    return program.check_downloader()
