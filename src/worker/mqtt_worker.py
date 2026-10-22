from aiomqtt import Client
from core.settings import settings
from telemetry.service import save_telemeter_in_database
from database.core import LocalAsyncSession
import asyncio
import ast



async def main():
    async with Client(settings.mqtt_broker) as client:
        await client.subscribe("Temperature")
        async for message in client.messages:
            data = message.payload 
            decode_data = data.decode("utf-8")
            data_dict = ast.literal_eval(decode_data)
            async with LocalAsyncSession() as db:
                data_save = await save_telemeter_in_database(data_dict.get("token"),
                                                    data_dict.get("odczyt_temperatury"),
                                                    data_dict.get("odczyt_wilgotnosc"),
                                                    db 
                                                    )
            if not data_save:
                print("Token cant be verify")
            else: 
                print(data_save)
                 
if __name__ == "__main__":
   with asyncio.Runner(loop_factory=asyncio.SelectorEventLoop) as runner:
            runner.run(main())
