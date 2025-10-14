from typing import Dict, Any, List
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class AgentKitAdapter:
    """Adapter for OpenAI AgentKit platform integration"""
    
    def __init__(self):
        self.agents = {}
        self.workflows = {}
        self.api_key = None  # To be configured by user
        
    async def initialize(self, config: Dict[Any, Any]):
        """Initialize AgentKit adapter with configuration"""
        self.api_key = config.get('api_key')
        logger.info("AgentKit adapter initialized")
        
    async def create_agent(self, agent_config: Dict[Any, Any]) -> Dict[Any, Any]:
        """Create an AgentKit agent"""
        agent_id = str(uuid.uuid4())
        agent = {
            'id': agent_id,
            'name': agent_config.get('name', 'Unnamed Agent'),
            'type': agent_config.get('type', 'creative'),
            'capabilities': agent_config.get('capabilities', []),
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'platform': 'agentkit'
        }
        
        self.agents[agent_id] = agent
        logger.info(f"Created AgentKit agent: {agent['name']}")
        return agent
    
    async def execute_agent(self, agent_id: str, input_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Execute an AgentKit agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        
        # Execute agent using real AgentKit SDK
        try:
            from services.agentkit_sdk_client import AgentKitSDKClient
            from models.agentkit_models import AgentExecutionRequest
            
            # Initialize real AgentKit client
            agentkit_client = AgentKitSDKClient(api_key=self.api_key)
            
            # Create execution request
            execution_request = AgentExecutionRequest(
                agent_id=agent_id,
                input_data=input_data,
                organization_id="default"  # Would be passed from context
            )
            
            # Execute agent
            result = await agentkit_client.execute_agent(agent_id, execution_request)
            
            return {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'input': input_data,
                'output': {
                    'status': 'completed',
                    'message': f"Agent {agent['name']} processed the request successfully",
                    'result': result.get('output_data', {}),
                    'execution_id': result.get('execution_id'),
                    'execution_time': result.get('execution_time_seconds', 0)
                },
                'timestamp': datetime.utcnow().isoformat(),
                'platform': 'agentkit'
            }
            
        except Exception as e:
            logger.error(f"AgentKit execution failed: {str(e)}")
            return {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'input': input_data,
                'output': {
                    'status': 'error',
                    'message': f"Agent execution failed: {str(e)}",
                    'result': None
                },
                'timestamp': datetime.utcnow().isoformat(),
                'platform': 'agentkit'
            }
        
        return result
    
    async def create_workflow(self, workflow_config: Dict[Any, Any]) -> Dict[Any, Any]:
        """Create a visual workflow in AgentKit"""
        workflow_id = str(uuid.uuid4())
        workflow = {
            'id': workflow_id,
            'name': workflow_config.get('name', 'Unnamed Workflow'),
            'steps': workflow_config.get('steps', []),
            'agents': workflow_config.get('agents', []),
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'platform': 'agentkit'
        }
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Created AgentKit workflow: {workflow['name']}")
        return workflow
    
    async def list_agents(self) -> List[Dict[Any, Any]]:
        """List all AgentKit agents"""
        return list(self.agents.values())
    
    async def get_agent_status(self, agent_id: str) -> Dict[Any, Any]:
        """Get status of an AgentKit agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        return {
            'agent': self.agents[agent_id],
            'health': 'healthy',
            'last_execution': datetime.utcnow().isoformat()
        }

agentkit_adapter = AgentKitAdapter()