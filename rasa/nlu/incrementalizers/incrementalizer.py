from typing import Dict, Text, Any, List

from typing import List, Type, Dict, Text, Any, Optional
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
import abc

ADD = "ADD"
REVOKE = "REVOKE"
COMMIT = "COMMIT"


# TODO: Correctly register your component with its type
@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)

class Incrementalizer(GraphComponent):
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        # TODO: Implement this
        return cls(config, execution_context.node_name)

    def __init__(
        self,
        config: Dict[Text, Any],
        name: Text,
    ) -> None:
        self.full_message = ""
        self.add_key = config['ADD_Key']
        self.revoke_key = config['REVOKE_Key']
        self.commit_key = config['COMMIT_Key']
        self.default_key = config['Default_Key']
        """Constructs a new byte pair vectorizer."""


    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {
            "ADD_Key": "/ADD",
            "REVOKE_Key": "/REVOKE",
            "COMMIT_Key": "/COMMIT",
            "Default_Key": COMMIT
        }

    # def train(self, training_data: TrainingData) -> Resource:
    #     # TODO: Implement this if your component requires training
    #     ...
    
    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            message = self.extract_IU_command(message)
            message = self.update_message_with_IU_command(message,message.get('iu_command'))


            
        return messages

    def extract_IU_command(self, message: Message) -> Message:
        iu_message = message.get('text')
        
        #default IU_command is ADD
        iu_type = self.default_key

        if self.add_key in iu_message:
            iu_type = ADD
            iu_message=iu_message.replace(self.add_key,"")
        elif self.revoke_key in iu_message:
            iu_type = REVOKE
            iu_message=iu_message.replace(self.revoke_key,"")
        elif self.commit_key in iu_message:
            iu_type = COMMIT
            iu_message=iu_message.replace(self.commit_key,"")

        iu_message = iu_message.strip()

        #now update everything
        #message.set('text',iu_message)
        message.set('iu_message',iu_message)

        message.set('iu_command',iu_type)
        return message

    def update_message_with_IU_command(self, message: Message, iu_command: str) -> Message:

        if iu_command == ADD or iu_command == COMMIT:

            self.full_message += " " + message.get('iu_message')
            self.full_message = self.full_message.strip()
            message.set('text',self.full_message)


        if iu_command == REVOKE:
            if message.get('iu_message') in self.full_message and message.get('iu_message') != "":
                #replaces the last occurance of the REVOKE message
                self.full_message = "".join(self.full_message.rsplit(message.get('iu_message'), 1)).replace("  ", " ")
                self.full_message = self.full_message.strip()
                message.set('text',self.full_message)

            else:
                #rasa.shared.utils.io.raise_warning(
                #"IU unit \"{}\" not found in \"{}\"... Aborting".format(message.iu_message,self.incrimental_full_message)
                message.set('text',self.full_message)
                pass
    
    
        if iu_command == COMMIT:

            #set text to full message
            message.set('text',self.full_message)
            #clear the current message out for next run
            self.full_message = ""