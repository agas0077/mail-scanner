# Third Party Library
from core.MailScanner.MailScanner import MailMonitor

# def upload_files_to_sp(file_list, sp_folder):
#     """Выгружает файлы на SP."""
#     logger.info("Отправка файлов на SharePoint.")

#     ctx = ShareOps(SP_URL)
#     ctx.authenticate(SP_CID, SP_SECRET)

#     bar = alive_bar(len(file_list))
#     with bar as bar:
#         for path in file_list:
#             bar()
#             try:
#                 ctx.upload_file(
#                     sp_folder,
#                     os.path.basename(path),
#                     path,
#                 )
#             except ClientRequestException as e:
#                 logger.critical(e)
#                 sys.exit()


# def sync_share_point(file_list):
#     """
#     Получает список файлов, которые надо дозалить на SP
#     и которые надо добавить в общий файл путем сравнения
#     списка уже существующих файлов на SP и того, что выкачели из
#     почты.
#     """
#     logger.info("Синхронизация с SharePoint.")

#     local_file_names = set(os.path.basename(path) for path in file_list)
#     ctx = ShareOps(SP_URL)
#     ctx.authenticate(SP_CID, SP_SECRET)
#     folder = ctx.get_folder(SP_FOLDER)
#     files = ctx.list_files(folder)

#     sp_file_names = set(file.properties["Name"] for file in files)
#     to_update_paths = [
#         path
#         for path in file_list
#         if os.path.basename(path) in local_file_names - sp_file_names
#     ]
#     return to_update_paths


def mail_monitor(server, email, password, search_string):
    mail = MailMonitor(server, email, password)
    ids = mail.search_mail(search_string)

    # paths = mail.download_attachments(
    #     (["get_filename", "сума"], ["get_filename", "СУМА"]),
    #     TEMP_FOLDER_PATH,
    #     all_any="any",
    # )
    # return paths
    return ids


def launch_mail_monitor(server, email, password, search_string, job_id):
    """
    Главная функция. Запускает в нужной последовательности все операции.
    """
    print(server, email, password, search_string)
    file_list = mail_monitor(
        server, email, password, search_string
    )  # Просматривает почту и скачивает файлы
    # update_file_list = sync_share_point(
    #     file_list
    # )  # Проверяет наличие файлов на SP
    # upload_files_to_sp(
    #     update_file_list, SP_FOLDER
    # )  # Догружает недостающие файлы на SP
    # return file_list
    print(email, file_list)
