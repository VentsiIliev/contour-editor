"""
Description:
    This module handles the serialization and persistence of workpieces data in JSON format.
    Workpieces are stored in a structured directory format based on date and timestamp,
    enabling easy versioning and tracking of saved workpieces.

    It expects workpieces classes to inherit from JsonSerializable to enable proper
    (de)serialization.
"""

import os
import json
import numpy as np
import datetime
from enum import Enum
from typing import Type
import copy
import shutil

from API.shared.workpiece.Workpiece import WorkpieceField
from API.shared.interfaces.JsonSerializable import JsonSerializable


class WorkpieceJsonRepository:
    """
      A repository for loading and saving workpieces data from/to JSON files.

      Attributes:
          DATE_FORMAT (str): Format for date directories.
          TIMESTAMP_FORMAT (str): Format for unique timestamped folders.
          FOLDER_NAME (str): Subdirectory name where workpieces are stored.
          WORKPIECE_FILE_SUFFIX (str): Suffix used in JSON workpieces file names.
      """
    DATE_FORMAT = "%Y-%m-%d"
    TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S-%f"
    FOLDER_NAME = "workpieces"
    WORKPIECE_FILE_SUFFIX = "_workpiece.json"  # Ensure the files have this suffix

    def __init__(self, baseDir, fields, dataClass):
        """
              Initializes the repository and attempts to load existing data.

              Args:
                  baseDir (str): Root directory where the workpieces folder exists.
                  fields (list): Expected fields for workpieces validation or display.
                  dataClass (Type): Class type implementing JsonSerializable.

              Raises:
                  TypeError: If `dataClass` is not a subclass of JsonSerializable.
                  FileNotFoundError: If the workpieces directory does not exist.
              """
        if not issubclass(dataClass, JsonSerializable):
            raise TypeError("dataClass must be a subclass of JsonSerializable")



        self.directory = os.path.join(baseDir, self.FOLDER_NAME)
        self.dataClass = dataClass
        self.fields = fields
        # check if dataClass is JsonSerializable

        self.data = self.loadData()
        self.visited_dirs = set()  # Track visited directories to avoid repetition
        if not os.path.exists(self.directory):
            print(f"Directory {self.directory} does not exist.")
            raise FileNotFoundError(f"Directory {self.directory} not found.")


    def loadData(self):
        """
        Recursively iterates over all directories inside the base directory, deserializes all JSON files,
        and returns a list of objects of the provided class type (e.g., Workpiece).
        """
        objects = []

        # Check if the base directory exists
        if not os.path.exists(self.directory):
            print(f"Directory {self.directory} does not exist.")
            return objects
        else:
            # print(f"Directory exists: {self.directory}")
            pass
        # print(f"Directory: {self.directory}")
        # Walk through all subdirectories and files
        for root, _, files in os.walk(self.directory):
            # print(f"Root: {root}")
            for file in files:
                # print(f"File: {file}")
                file_path = os.path.join(root, file)
                # print(f"File Path: {file_path}")  # Debugging: check the full file path
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)  # Load JSON data
                        print(f"Loaded Data: {data}")  # Debugging: Show the loaded data
                        obj = self.dataClass.deserialize(data)  # Deserialize into the appropriate object
                        # print(f"Deserialized Object: {obj}")  # Debugging: Show the deserialized object
                        objects.append(obj)
                except Exception as e:
                    print(f"Error loading object from {file_path}: {e}")
                    raise Exception(f"Error loading object: {e}")

        return objects

    def saveWorkpiece(self, workpiece):
        print("Saving workpiece:", workpiece)
        """
              Saves a workpieces object as a JSON file in a timestamped folder structure.

              Args:
                  workpiece (JsonSerializable): The workpieces object to save.

              Returns:
                  tuple: (bool, str) where bool indicates success, and str contains a message.

              Raises:
                  Exception: If file writing fails.
              """
        print("Saveing workpiece with contour: ",workpiece.contour)
        # Get today's date and timestamp
        today_date = datetime.datetime.now().strftime(self.DATE_FORMAT)
        timestamp = datetime.datetime.now().strftime(self.TIMESTAMP_FORMAT)

        # Full path based on today's date
        date_dir = os.path.join(self.directory, today_date)
        timestamp_dir = os.path.join(date_dir, timestamp)

        # Check if the folder for today's date exists, if not, create it
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        # Create the folder with the timestamp if it doesn't exist
        os.makedirs(timestamp_dir, exist_ok=True)

        # Serialize the workpieces
        serialized_data = json.dumps(self.dataClass.serialize(copy.deepcopy(workpiece)), indent=4)
        print("Serialized Data: ", serialized_data)
        # Define the file path
        file_path = os.path.join(timestamp_dir, f"{timestamp}{self.WORKPIECE_FILE_SUFFIX}")

        try:
            # Save the workpieces to the file
            with open(file_path, 'w') as file:
                file.write(serialized_data)
            # workpieces.sprayPattern = np.array(workpieces.sprayPattern).reshape(-1, 1, 2).astype(np.int32)
            self.data.append(workpiece)
            # print(f"Workpiece saved to {file_path}")

            return True,"Workpiece saved successfully"
        except Exception as e:
            raise Exception(e)
            # print(f"Error saving workpieces: {e}")

    def deleteWorkpiece(self, workpieceId):
        """
        Deletes a workpiece by its ID from the repository and filesystem.

        Args:
            workpieceId (str): The ID of the workpiece to delete.
            
        Returns:
            tuple: (bool, str) where bool indicates success, and str contains a message.
            
        Raises:
            Exception: If workpiece not found or deletion fails.
        """
        print(f"WorkpieceJsonRepository.deleteWorkpiece called with ID: {workpieceId}")
        print(f"Repository data length: {len(self.data) if self.data else 'None'}")
        try:
            # Find the workpiece in the data list
            workpiece_to_delete = None
            workpiece_index = None
            
            for i, workpiece in enumerate(self.data):
                if hasattr(workpiece, 'workpieceId') and str(workpiece.workpieceId) == str(workpieceId):
                    workpiece_to_delete = workpiece
                    workpiece_index = i
                    print(f"Workpiece found in memory: {workpiece}")
                    break
            
            if workpiece_to_delete is None:
                return False, f"Workpiece with ID '{workpieceId}' not found."
            
            # Find and delete the corresponding file/directory on filesystem
            file_deleted = False
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    if file.endswith(self.WORKPIECE_FILE_SUFFIX):
                        file_path = os.path.join(root, file)
                        try:
                            # Load the file to check if it contains our workpiece
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                # Check if this file contains the workpiece we want to delete
                                file_workpiece_id = data.get('workpieceId') or data.get('id')
                                if str(file_workpiece_id) == str(workpieceId):
                                    # Delete the entire timestamp directory (contains the workpiece file)
                                    parent_dir = os.path.dirname(file_path)
                                    shutil.rmtree(parent_dir)
                                    print(f"Deleted workpiece directory: {parent_dir}")
                                    
                                    # Check if the date directory is also empty and delete it
                                    try:
                                        date_dir = os.path.dirname(parent_dir)
                                        if not os.listdir(date_dir):
                                            os.rmdir(date_dir)
                                            print(f"Deleted empty date directory: {date_dir}")
                                    except OSError:
                                        # Directory not empty or other issues, that's fine
                                        pass
                                    
                                    file_deleted = True
                                    break
                        except Exception as e:
                            print(f"Error checking file {file_path}: {e}")
                            continue
                
                if file_deleted:
                    break
            
            if not file_deleted:
                return False, f"Workpiece file for ID '{workpieceId}' not found on filesystem."
            
            # Remove from in-memory data
            self.data.pop(workpiece_index)
            
            return True, f"Workpiece '{workpieceId}' deleted successfully."
            
        except Exception as e:
            print(f"Error deleting workpiece {workpieceId}: {e}")
            return False, f"Error deleting workpiece: {str(e)}"

    def get_workpiece_by_id(self, workpieceId):
        """
        Retrieves a workpiece by its ID.

        Args:
            workpieceId (str): The ID of the workpiece to retrieve.

        Returns:
            JsonSerializable: The workpiece object if found, else None.
        """
        for workpiece in self.data:
            if hasattr(workpiece, 'workpieceId') and str(workpiece.workpieceId) == str(workpieceId):
                return workpiece
        return None