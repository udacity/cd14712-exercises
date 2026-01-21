## Smart Home MCP Architecture Exercise

### Introduction

Welcome to the MCP Architecture exercise! In this hands-on lab, you'll apply the architectural concepts you learned in Module 3 by designing an MCP-based smart home system.

#### Why a Smart Home System?

Smart homes provide an excellent analogy for understanding MCP architecture because they involve:
- **Multiple independent devices** (lights, thermostats, cameras) that mirror MCP servers
- **Central coordination** (smart home hub) that mirrors MCP hosts/clients
- **Standardized communication** protocols that mirror JSON-RPC
- **Real-world actions** that mirror MCP tools and resources

#### What You'll Learn

By completing this exercise, you'll gain practical experience in:
1. **Mapping real-world systems to MCP architecture** - Understanding how Hosts, Clients, and Servers relate
2. **Tracing communication patterns** - Following JSON-RPC message flows through the system
3. **Categorizing capabilities** - Identifying what should be a Tool, Prompt, or Resource
4. **Selecting appropriate transports** - Choosing between stdio and HTTP/SSE based on requirements

#### Your Scenario

You've been hired by "SmartLife Inc." to architect their next-generation smart home platform using MCP. The system needs to:
- Control various IoT devices (lights, locks, thermostats, cameras)
- Respond to voice commands through an AI assistant
- Execute complex routines (e.g., "Goodnight" turns off lights, locks doors, sets alarm)
- Provide real-time status updates to mobile apps

Your task is to design how this system would work using MCP principles.

#### Prerequisites

Before starting, make sure you understand:
- The three MCP roles (Host, Client, Server) from Lecture 3.1
- JSON-RPC 2.0 message format from Lecture 3.2
- Transport mechanisms (stdio vs HTTP/SSE) from Lecture 3.3
- MCP primitives (Tools, Prompts, Resources) from Module 5

#### Deliverables

By the end of this exercise, you'll submit:
1. An architectural diagram mapping smart home components to MCP roles
2. JSON-RPC message traces for two scenarios
3. A categorized list of capabilities as Tools, Prompts, and Resources
4. A transport mechanism selection matrix with justifications

---

## 1. Identify Smart Home Components and Map to MCP Roles

In this section, you'll identify the key components of a smart home system and map them to MCP's architectural roles.

### Tasks:

- **List the components of a Smart Home System**
  - Think about: Voice assistants, mobile apps, device controllers, individual devices, cloud services
  - Consider both physical devices and software services

- **Map to MCP architecture and visualize the relationship**: Create a visual diagram showing the mapping between Smart Home and MCP Components
  - Which component acts as the Host (AI application)?
  - Which component acts as the Client (coordinator)?
  - Which components act as Servers (capability providers)?

### Example to Get You Started:

```
Smart Home Component    →    MCP Role
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Voice Assistant (Alexa) →    Host
Smart Hub Controller    →    Client
Smart Light Bulb       →    Server
[Your additions here...]
```

---

## 2. Trace Communication Patterns Using JSON-RPC

Now you'll trace how commands flow through the system using JSON-RPC 2.0 protocol.

### Tasks:

- **Map a simple interaction**: Choose a basic command such as "Turn on living room lights" and trace the communication flow step-by-step
- **Identify request/response pairs**: For each step, note:
  - What request is sent
  - Who sends it (Host to Client, Client to Server)
  - What response comes back
- **Add a complex scenario**: Repeat the first steps but now for a more complex scenario such as "Start the Goodnight routine"

### Template for Your Trace:

#### Simple Scenario: "Turn on living room lights"

**Step 1: User speaks to voice assistant**
```json
// Host → Client
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "control_light",
    "arguments": {
      "room": "living_room",
      "action": "on"
    }
  },
  "id": 1
}
```

**Step 2: [Continue your trace...]**

---

## 3. Categorize Smart Home Capabilities into MCP Primitives

Map your smart home capabilities into **Resources**, **Prompts**, and **Tools**:

### Tasks:

- **Identify Resources**: Data that can be read/monitored
  - Example: Current temperature reading
  - Example: Security camera feed
  - [Add at least 5 more]

- **Identify Prompts**: Pre-configured scenarios or templates
  - Example: "Goodnight routine" template
  - Example: "Vacation mode" configuration
  - [Add at least 3 more]

- **Identify Tools**: Actions that can be executed
  - Example: turn_on_light(room, brightness)
  - Example: set_temperature(zone, temperature)
  - [Add at least 5 more]

### Categorization Table:

| Category | Item | Description | MCP Implementation |
|----------|------|-------------|-------------------|
| Resource | temperature/living_room | Current temperature reading | Read-only sensor data |
| Tool | control_light | Turn lights on/off | Function with parameters |
| Prompt | goodnight_routine | Bedtime automation | Template with multiple actions |
| [Your additions...] | | | |

---

## 4. Evaluate and Select Transport Mechanisms

Finally, you'll determine the best transport mechanism for each component connection.

### Tasks:

- **Analyze connection requirements**: For each device type, consider:
  - Is it always connected or intermittent?
  - Does it need real-time bidirectional communication?
  - Is it local network only or cloud-connected?
  - What's the expected message frequency?
  - Are there security/firewall considerations?

- **Match transport to use case**:
  - `stdio`: Best for local, always-running processes
  - `HTTP/SSE`: Best for network-accessible, potentially remote services

### Transport Selection Matrix:

| Connection | From | To | Transport | Justification |
|------------|------|----|-----------|---------------|
| Voice Commands | Alexa Host | Hub Client | HTTP/SSE | Cloud-based, needs remote access |
| Light Control | Hub Client | Light Server | stdio | Local network, always connected |
| [Your additions...] | | | | |

### Questions to Consider:

1. How would you handle a device that goes offline temporarily?
2. What transport would you use for a battery-powered sensor that wakes up periodically?
3. How would you secure communications for door locks and security systems?
4. Would you use different transports for local vs. remote control of the same device?

---

## Submission Guidelines

1. Create a single document with all four sections completed
2. Include your architectural diagram (can be hand-drawn and scanned, or use any diagramming tool)
3. Provide complete JSON-RPC examples for both scenarios in Section 2
4. Justify all transport selections with specific technical reasons
5. Be prepared to discuss your design choices in class

## Grading Rubric

- **Section 1 (25%)**: Comprehensive component list and accurate MCP role mapping
- **Section 2 (25%)**: Correct JSON-RPC format and logical message flow
- **Section 3 (25%)**: Appropriate categorization with clear explanations
- **Section 4 (25%)**: Well-reasoned transport selections with technical justification

## Bonus Challenge (Optional)

Design how your smart home system would handle:
1. A power outage affecting some devices
2. Multiple users with different permission levels
3. Integration with external services (weather, calendar, etc.)

Good luck with your smart home MCP architecture design!