"""
Firebase Service
Handles all Firebase Firestore operations including authentication and data management
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import SERVER_TIMESTAMP
import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        """Initialize Firebase connection"""
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get Firebase configuration from environment variables
                firebase_config = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n') if os.getenv('FIREBASE_PRIVATE_KEY') else None,
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
                }
                
                # Initialize Firebase app
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            # For development, use emulator or mock
            logger.warning("Using Firebase emulator or mock for development")
            self.db = None
    
    def get_timestamp(self):
        """Get server timestamp"""
        return SERVER_TIMESTAMP
    
    # Document operations
    def create_document(self, collection: str, document_id: Optional[str], data: Dict[str, Any]):
        """Create a new document"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            collection_ref = self.db.collection(collection)
            
            if document_id:
                doc_ref = collection_ref.document(document_id)
                doc_ref.set(data)
            else:
                doc_ref = collection_ref.add(data)[1]
                
            logger.info(f"Document created in {collection}: {doc_ref.id}")
            return doc_ref
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get_document(self, collection: str, document_id: str):
        """Get a document by ID"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]):
        """Update a document"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            
            logger.info(f"Document updated in {collection}: {document_id}")
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise
    
    def delete_document(self, collection: str, document_id: str):
        """Delete a document"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            self.db.collection(collection).document(document_id).delete()
            logger.info(f"Document deleted from {collection}: {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_collection(self, collection: str):
        """Get a collection reference"""
        if not self.db:
            raise Exception("Firebase not initialized")
        return self.db.collection(collection)
    
    def query_documents(self, collection: str, filters: List[tuple] = None, limit: int = None):
        """Query documents with filters"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            query = self.db.collection(collection)
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.get()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
                
            return results
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise
    
    # Authentication operations
    def create_user(self, email: str, password: str, display_name: str = None):
        """Create a new user"""
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            logger.info(f"User created: {user_record.uid}")
            return user_record
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def verify_id_token(self, id_token: str):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise
    
    def get_user(self, uid: str):
        """Get user by UID"""
        try:
            user_record = auth.get_user(uid)
            return user_record
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise
    
    def delete_user(self, uid: str):
        """Delete user by UID"""
        try:
            auth.delete_user(uid)
            logger.info(f"User deleted: {uid}")
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    # Batch operations
    def batch_write(self, operations: List[Dict]):
        """Execute batch write operations"""
        try:
            if not self.db:
                raise Exception("Firebase not initialized")
                
            batch = self.db.batch()
            
            for operation in operations:
                op_type = operation['type']
                collection = operation['collection']
                doc_id = operation['document_id']
                doc_ref = self.db.collection(collection).document(doc_id)
                
                if op_type == 'set':
                    batch.set(doc_ref, operation['data'])
                elif op_type == 'update':
                    batch.update(doc_ref, operation['data'])
                elif op_type == 'delete':
                    batch.delete(doc_ref)
            
            batch.commit()
            logger.info(f"Batch operation completed: {len(operations)} operations")
            
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            raise
