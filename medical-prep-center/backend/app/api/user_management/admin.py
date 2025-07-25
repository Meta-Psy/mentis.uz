# === Загрузка и управление материалами для студента ===


@router.post("/upload")
async def upload_material_file(
    file: UploadFile = File(...),
    category: str = Query(..., regex="^(book|test|video|other)$"),
    module_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Загрузка файла материала (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Проверяем тип файла
        allowed_extensions = {".pdf", ".doc", ".docx", ".mp4", ".avi", ".mkv"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый тип файла"
            )
        
        # Создаем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Сохраняем информацию о файле в базе данных
        file_info = {
            "filename": safe_filename,
            "original_name": file.filename,
            "size": len(content),
            "category": category,
            "module_id": module_id,
            "topic_id": topic_id,
            "uploaded_by": current_user.user_id,
            "upload_date": datetime.now()
        }
        
        # Здесь должна быть логика сохранения в базу данных
        # save_material_file_info(file_info)
        
        return {
            "message": "Файл успешно загружен",
            "file_id": safe_filename,
            "download_url": f"/api/v1/materials/download/{safe_filename}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_material_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Скачивание файла материала"""
    try:
        file_path = UPLOAD_DIR / file_id
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
        
        # Получаем оригинальное имя файла из базы данных
        # file_info = get_material_file_info(file_id)
        # original_name = file_info.original_name if file_info else file_id
        
        return FileResponse(
            path=file_path,
            filename=file_id,  # В реальности использовать original_name
            media_type='application/octet-stream'
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/files/{file_id}")
async def delete_material_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Удаление файла материала (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        file_path = UPLOAD_DIR / file_id
        
        if file_path.exists():
            os.remove(file_path)
        
        # Удаляем информацию из базы данных
        # delete_material_file_info(file_id)
        
        return {"message": "Файл успешно удален"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ ВИДЕОУРОКАМИ =====

@router.post("/videos")
async def add_video_lesson(
    video_data: AddVideoLessonRequest,
    current_user = Depends(get_current_user)
):
    """Добавление видеоурока к теме (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика добавления видеоурока через topic_service
        # update_topic_video(video_data.topic_id, video_data.video_url)
        
        return {"message": "Видеоурок добавлен"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sections/{section_id}/materials")
async def add_section_materials(
    section_id: int,
    materials_data: AddSectionMaterialsRequest,
    current_user = Depends(get_current_user)
):
    """Добавление материалов к разделу (только для учителей и администраторов)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям и администраторам"
        )
    
    try:
        # Логика добавления материалов через section_service
        # add_section_material_links(section_id, materials_data.links)
        
        return {"message": "Материалы добавлены к разделу"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

