if __name__ == "__main__":

    # # 1. tuple 表
    # from langchain_core.prompts import ChatPromptTemplate

    # prompt=ChatPromptTemplate.from_messages([
    #     ("system","你是一个助手"),
    #     ("human","{user_message}")
    # ])
    # print(prompt)

    # # 2. 消息对象列表
    # from langchain_core.prompts import ChatPromptTemplate
    # from langchain_core.messages import SystemMessage
    # from langchain_core.prompts import HumanMessagePromptTemplate

    # prompt = ChatPromptTemplate.from_messages([
    #     SystemMessage(content="你是一个助手"),
    #     HumanMessagePromptTemplate.from_template("{user_message}")
    # ])

    # print(prompt)

    # 3. 多轮对话
    # from langchain_core.prompts import ChatPromptTemplate
    # from langchain_core.prompts import MessagesPlaceholder

    # prompt = ChatPromptTemplate.from_messages([
    #     ("system","你是一个助手"),
    #     MessagesPlaceholder("history"),
    #     ("human","{user_message}")
    # ])

    from app.services.llm_client import get_llm
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.prompts import MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system","你是一个助手"),
        MessagesPlaceholder("history"),
        ("human","{user_message}")
    ])
    chain = prompt | llm | StrOutputParser()
    print(prompt.input_variables)  # ['history', 'user_message']
    # print(chain.invoke({ 
    #     "user_message":"你好，我是谁",
    #     "history":[
    #         ("human","你好，我是游"),
    #         ("ai","好的，游")
    #     ]
    # }))
    pass