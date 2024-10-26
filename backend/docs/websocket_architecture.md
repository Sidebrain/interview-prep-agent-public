# Websocket Architecture think through

Ok I am about to create a complex state object in react with a fairly detailed object type. This type is representing an object that I will be receiving from the backend via a websocket string. I will be taking the websocket object and parsing it for a type. Based on the type I want to be doing the routing. 

Here is a loose definition of what will be received from tbe backend

```ts
type WebsocketMessage = {
    messageId: str // this will be the message id it is meant for. multiple messages might be in play and internal states of multiple may be mutating around the same time due to async communication
    address: str // this will be the routing key similar to the address in a courier delivery, for example it could be the field name of the object that needs to be updated. Or it could map to a dispatch strategy. What do you think?
    payload: MessageType | LogsType | CitationsType  // these are the various components they can populate. The address and the payload will be a disambiguated type (is that right?)
}
```

Now each one of these payload types will match the props as closely as required (not needing the parts that can be supplied by the client) and I am planning to use the address to route to the appropriate state in react. I will set up each state with a reducer so I can do complex state updates and use the dispatch as an effective state machine. 

Comment on my strategy, tell me where I need to bolster my thinking. My primary purpose is to build a scalable websocket exchange platform with a particular focus on the backend to frontend messaging protocol. I want the schema on both sides to allow scalability as I dont want to be stuck later on. The message protocol should support new components being added, and the message being intended for different states. 

Also tell me if a MessageType is the shape of a state, something like

```typescript
type MessageType = {
    sources: string[],
    messageId: string, 
    content: string,
    followUpQuestions: string[]
}
```

then if I use async streaming with bits and pieces coming in and it uploads different parts of the message state, then on the frontend if I have a big component that depends on a bunch of smaller components which depend on each of the fields like `sources` `content` `followUpQuestions` then would all of them stream paralleley?

Help answer all the questions I asked in my writeup

## How would this look without rabbitmq

The frontend which is in react nextjs with typescript and fastapi backend.

we want to route based on action_type on the message packet. I will maintain an internal dictionary of key: string to an action, which is a state dispatch function. 