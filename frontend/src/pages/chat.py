import streamlit as st
import json
import time
import re
from src.modules.util import send_message, create_chat, get_chat_messages, get_schema, get_warehouse, get_warehouses

from src.pages.base import BasePage

from src.dialogs.dataset_modal import DatasetModal
from src.dialogs.warehouse_modal import WarehouseModal
from src.dialogs.chat_history_modal import ChatHistoryModal
from src.components.charts.chart_registry import ChartRegistry

class ChatPage(BasePage):
    def __init__(self):
        self.warehouses = get_warehouses(st.session_state['token'])
        self.agent_id = st.session_state.ids['agent_id']        
        self.model_id = st.session_state.ids['model_id']

        self.chat_id = st.session_state.ids.get('chat_id') or st.query_params.get('chat_id')
        if self.chat_id:
            st.session_state.ids['chat_id'] = self.chat_id
            st.query_params.update(chat_id = self.chat_id)

        self.render()
    
    def _display_messages(self):
        for message in st.session_state.messages:
            if message['sender'] == 'user':
                for item in message['payload']['input']:
                    if item['role'] != 'developer':
                        with st.chat_message('user'):
                            st.write(item['content'])
            else:
                with st.chat_message('assistant'):
                    input = []
                    payload = message.get('payload', '[]')
                    for response in payload:
                        if response['type'] != 'function_call_output':
                            outputs = response['response'].get('output', [])
                            for output in outputs:
                                if output['type'] == 'message':
                                    for item in output['content']:
                                        if item['type'] == 'output_text':
                                            self._render_text(item['text'])
                        else:
                            if response['tool_name'] == 'create_chart':
                                chart_config = response['output']['result']
                                chart_kind = chart_config['kind']
                                chart_class = ChartRegistry.get_chart(chart_kind)
                                chart_class(
                                    st.session_state.token,
                                    chart_config["x"],
                                    chart_config["y"],
                                    chart_config["categories"],
                                    chart_config["query"],
                                    chart_config["warehouse_id"],
                                    chart_config["title"]
                                )

    def _render_text(self, text: str, holder=st):
        pattern = r'\\\[(.*?)\\\]'
        matches = re.findall(pattern, text, re.DOTALL)
        pos = [{'match': match, 'start': text.index(match), 'length': len(match)} for match in matches]
        cleaned_text = text
        for i, it in enumerate(pos):
            cleaned_text = cleaned_text.replace(it['match'], f'FORMULA')
        text_chunks = cleaned_text.split('\[FORMULA\]')

        for i in range(len(pos)):
            holder.write(text_chunks[i])
            if len(pos) > i:
                holder.latex(pos[i]['match'])
        holder.write(text_chunks[-1])

    def render(self):

        warehouse_col, _, memory_col, attachment_col, new_col, hist_col = st.columns([0.50, 0.3, 0.05, 0.05, 0.05, 0.05])


        if len(self.warehouses) > 0:
            new_warehouse_col, dropdown_col = warehouse_col.columns([0.15, 0.85])
            if new_warehouse_col.button('', icon=':material/add:', type='primary', use_container_width=True):
                WarehouseModal(destination='Chat')
            warehouse_name = dropdown_col.selectbox('Warehouse', [warehouse['name'] for warehouse in self.warehouses], label_visibility='collapsed')
            warehouse_id = [warehouse['id'] for warehouse in self.warehouses if warehouse['name'] == warehouse_name][0]
            if attachment_col.button('', icon=':material/attach_file:', type='tertiary'):
                DatasetModal(warehouse_id, destination='Chat')
        else:

            warehouse_id = None
            if warehouse_col.button('Create Warehouse', type='primary'):
                WarehouseModal(destination='Chat')
        
        # if memory_col.button('', use_container_width=True, icon=":material/memory:", key='memory_chat', type='tertiary'):
        #     st.toast('Feature not available yet')

        if new_col.button('', use_container_width=True, icon=":material/add_circle:", key='new_chat', type='tertiary'):
            st.session_state.ids['chat_id'] = None
            st.session_state.messages = []
            st.query_params.clear()
            st.rerun()
        
        if hist_col.button('', use_container_width=True, icon=":material/history:", key='history_chat', type='tertiary'):
            ChatHistoryModal()

        st.markdown('<div style="margin-bottom: 40px;"><div>', unsafe_allow_html=True)

        welcome_placeholder = st.empty()
        if self.chat_id is not None:
            st.session_state.messages = get_chat_messages(st.session_state['token'], self.chat_id)
        else:
            welcome_placeholder.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center; min-height: 55vh;">
                    <div style="text-align: center;">
                        <p style="font-size: 3.5rem; margin: 0; margin-bottom: 0px; padding: 0px;">Hello, {st.session_state.user['name']}</p>
                        <span style="font-size: 1.4rem; color: #666; margin: 0; padding: 0px;">How can I help you today?</span>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        self._display_messages()

        if prompt := st.chat_input("What would you like to ask?"):

            welcome_placeholder.empty()
            
            st.chat_message('user').markdown(prompt)

            payload = {
                "model": self.model_id,
                "input": [
                    {"role": "user", "content": prompt}
                ]
            }

            if self.chat_id is None:
                self.chat_id = create_chat(st.session_state['token'])['id']
                st.session_state.ids['chat_id'] = self.chat_id

            for chunk in send_message(st.session_state['token'], self.chat_id, self.agent_id, payload, {'warehouse_id': warehouse_id}):
                
                event = chunk['event']
                data = chunk['data']

                if event == 'internal.process.started':
                    assistant_message = st.chat_message('assistant')

                elif event == 'response.created':
                    pass

                elif event == 'internal.process.tool_execution_started':
                    tool_message_placeholder = assistant_message.empty()
                    tool_name = data['tool_name']
                    tool_message_placeholder.markdown(f'*Executing tool: {tool_name}*')
                    time.sleep(5)

                elif event == 'internal.process.tool_execution_completed':
                    tool_name = data['tool_name']
                    tool_arguments = data['arguments']
                    tool_result = data['result']
                    tool_message_placeholder.markdown(f'*Tool {tool_name} completed*')
                    with assistant_message.expander('Tool result'):
                        st.write('Arguments')
                        st.json(tool_arguments)
                        st.write('Result')
                        st.json(tool_result)
                    
                    if tool_name == 'create_chart':
                        chart_config = tool_result['result']
                        chart_kind = chart_config['kind']
                        chart_class = ChartRegistry.get_chart(chart_kind)
                        with assistant_message:
                            chart = chart_class(
                                st.session_state.token,
                                chart_config["x"],
                                chart_config["y"],
                                chart_config["categories"],
                                chart_config["query"],
                                chart_config["warehouse_id"],
                                chart_config["title"]
                            )
                        
                elif event == 'response.content_part.added':
                    placeholder = assistant_message.empty()

                elif event in 'response.output_text.delta':
                    output = data['response']['output']
                    for item in output:
                        for content in item['content']:
                            if content['type'] == 'output_text':
                                placeholder.markdown(content['text'])
                
                elif event == 'internal.process.completed':
                    st.rerun()

ChatPage()