# Agentopy (wip)

Lightweight, modular, extensible framework for building agents and environments. 

# How it works

Essetially there are the following pieces:

1. **Agent** - represents the agent, it takes in the environment, a list of components and a policy. It is implemented as a class of `IAgent` interface, it has a state and a policy. Agent can be in one of the following state: observing - get the evironment state and update the agent state, thinking - use the policy to select the next action to perform based on the agent state, acting - perform the action, idle - stay idle for given period.
2. **EnvironmentComponent** - represents a component of the environment, it defines part of the environment state and actions that can be performed on it. It is implemented as a class of `IEnvironmentComponent` interface, it has a state and a list of actions, each action is implemented as a member function of the component, it can be stateful or stateless. It implements the on_tick method that is called by the environment on each tick. It can be used to update the component state.
3. **AgentComponent** - represents a component of the agent, it defines part of the agent state and actions that can be performed on it. It is implemented as a class of `IAgentComponent` interface, it has a state and a list of actions, each action is implemented as a member function of the component, it can be stateful or stateless. It implements the on_heartbeat method that is called by the agent on each heartbeat. It can be used to update the component state and the agent state.
3. **Environment** - represents the environment, it takes in a list of components. It is implemented as a class of `IEnvironment` interface, it has a state and a list of components. It implements the `tick` method that is called with given period, which calls the `on_tick` method of each component. 
4. **Policy** - represents the policy, it takes in the agent state and returns the next action to perform. It is implemented as a class of `IPolicy` interface.
5. **Action** - represents an action that can be executed by the agent, it is implemented as a member function of the component and wrapped in the `Action` class.
6. **State** - represents the state of the agent or the environment, it is implemented as a class of `IState` interface. It is a dictionary of key-value pairs.
