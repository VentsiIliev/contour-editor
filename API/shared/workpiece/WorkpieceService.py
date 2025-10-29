"""
Description:
    The WorkpieceService class acts as a service layer for interacting with
    the workpieces repository. It provides methods to save and load workpieces,
    serving as an abstraction between the business logic and data access layers.
"""

from GlueDispensingApplication.workpiece.Workpiece import Workpiece
from GlueDispensingApplication.workpiece.WorkPieceRepositorySingleton import WorkPieceRepositorySingleton

class WorkpieceService:
    """
       A service class for managing workpieces through a singleton repository instance.

       Attributes:
           DATE_FORMAT (str): Format for date-based folder naming.
           TIMESTAMP_FORMAT (str): Format for timestamp-based subfolder naming.
           BASE_DIR (str): Directory path for storing workpieces JSON files.
           WORKPIECE_FILE_SUFFIX (str): Suffix used for naming saved workpieces files.
       """
    DATE_FORMAT = "%Y-%m-%d"
    TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S-%f"
    BASE_DIR = "GlueDispensingApplication/storage/workpieces"
    WORKPIECE_FILE_SUFFIX = "_workpiece.json"

    def __init__(self):
        """
              Initializes the WorkpieceService by obtaining the singleton instance
              of the workpieces repository.
              """
        self.repository = WorkPieceRepositorySingleton().get_instance()

    def saveWorkpiece(self, workpiece: Workpiece):
        """
                Saves a given workpieces using the repository.

                Args:
                    workpiece (Workpiece): The workpieces object to save.

                Returns:
                    tuple: (bool, str) indicating success status and a message.
                """
        return self.repository.saveWorkpiece(workpiece)

    def loadAllWorkpieces(self):
        """
            Loads all previously saved workpieces from the repository.

            Returns:
                list: A list of Workpiece objects.
            """
        data = self.repository.data
        return data

    def deleteWorkpiece(self, workpieceId):
        """
            Deletes a workpiece by its ID using the repository.

            Args:
                workpieceId (str): The ID of the workpiece to delete.

            Returns:
                tuple: (bool, str) indicating success status and a message.
            """
        print(f"WorkpieceService deleting workpiece with ID: {workpieceId}")
        print(f"WorkpieceService repository type: {type(self.repository)}")
        result = self.repository.deleteWorkpiece(workpieceId)
        print(f"WorkpieceService deleteWorkpiece result: {result}")
        return result

    def get_workpiece_by_id(self, workpieceId):
        """
            Retrieves a workpiece by its ID.

            Args:
                workpieceId (str): The ID of the workpiece to retrieve.

            Returns:
                Workpiece or None: The Workpiece object if found, else None.
            """
        return self.repository.get_workpiece_by_id(workpieceId)

    # To save a new workpiece, create an instance of Workpiece and call saveWorkpiece
    # new_workpiece = Workpiece(...)
    # service.saveWorkpiece(new_workpiece)