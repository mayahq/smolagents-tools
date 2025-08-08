"""
Planning and task management tool adapted for smolagents
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import AsyncSmolTool, SmolToolResult


class PlanningTool(AsyncSmolTool):
    """
    A tool for creating and managing task plans and workflows
    Adapted from OpenManus PlanningTool
    """
    
    def __init__(self):
        self.name = "planning"
        self.description = """A tool for creating, managing, and tracking task plans and workflows. Can break down complex tasks into subtasks."""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: create_plan, add_task, update_task, complete_task, get_plan, analyze_task",
                "required": True
            },
            "task_description": {
                "type": "string",
                "description": "Description of the main task or goal (required for create_plan and analyze_task)",
                "required": False
            },
            "plan_id": {
                "type": "string",
                "description": "ID of the plan to work with (required for most actions except create_plan)",
                "required": False
            },
            "task_id": {
                "type": "string",
                "description": "ID of specific task within plan (required for update_task, complete_task)",
                "required": False
            },
            "subtask_title": {
                "type": "string",
                "description": "Title for new subtask (required for add_task)",
                "required": False
            },
            "subtask_description": {
                "type": "string",
                "description": "Description for new subtask (required for add_task)",
                "required": False
            },
            "priority": {
                "type": "string",
                "description": "Priority level: high, medium, low",
                "default": "medium",
                "required": False
            },
            "estimated_time": {
                "type": "string",
                "description": "Estimated time to complete (e.g., '2 hours', '30 minutes')",
                "required": False
            },
            "dependencies": {
                "type": "string",
                "description": "Comma-separated list of task IDs this task depends on",
                "required": False
            },
            "update_content": {
                "type": "string",
                "description": "Content to update task with (for update_task action)",
                "required": False
            }
        }
        self.output_type = "string"
        
        # In-memory storage for plans (in real implementation, this would be persistent)
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._next_plan_id = 1
        self._next_task_id = 1
        super().__init__()
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID"""
        plan_id = f"plan_{self._next_plan_id}"
        self._next_plan_id += 1
        return plan_id
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        task_id = f"task_{self._next_task_id}"
        self._next_task_id += 1
        return task_id
    
    def _break_down_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Break down a complex task into subtasks using simple heuristics"""
        # This is a simplified version - in a real implementation, 
        # this could use LLM or more sophisticated analysis
        
        subtasks = []
        
        # Common task patterns and their breakdowns
        if "website" in task_description.lower() or "web app" in task_description.lower():
            subtasks = [
                {"title": "Plan and Design", "description": "Create wireframes and plan the structure"},
                {"title": "Setup Project", "description": "Initialize project structure and dependencies"},
                {"title": "Implement Frontend", "description": "Create user interface components"},
                {"title": "Implement Backend", "description": "Create server-side logic and APIs"},
                {"title": "Testing", "description": "Test functionality and fix bugs"},
                {"title": "Deployment", "description": "Deploy to production environment"}
            ]
        elif "api" in task_description.lower():
            subtasks = [
                {"title": "Design API", "description": "Define endpoints and data structures"},
                {"title": "Setup Framework", "description": "Initialize API framework and dependencies"},
                {"title": "Implement Endpoints", "description": "Create API endpoints and logic"},
                {"title": "Add Authentication", "description": "Implement security and authentication"},
                {"title": "Testing", "description": "Test API endpoints and functionality"},
                {"title": "Documentation", "description": "Create API documentation"}
            ]
        elif "data analysis" in task_description.lower() or "analysis" in task_description.lower():
            subtasks = [
                {"title": "Data Collection", "description": "Gather and prepare data sources"},
                {"title": "Data Cleaning", "description": "Clean and preprocess the data"},
                {"title": "Exploratory Analysis", "description": "Perform initial data exploration"},
                {"title": "Analysis", "description": "Conduct detailed analysis"},
                {"title": "Visualization", "description": "Create charts and visualizations"},
                {"title": "Report", "description": "Compile findings into a report"}
            ]
        else:
            # Generic breakdown
            subtasks = [
                {"title": "Research and Planning", "description": "Research requirements and plan approach"},
                {"title": "Setup and Preparation", "description": "Prepare tools and environment"},
                {"title": "Implementation", "description": "Execute the main work"},
                {"title": "Testing and Validation", "description": "Test and validate the results"},
                {"title": "Documentation", "description": "Document the process and results"}
            ]
        
        # Add IDs and metadata to subtasks
        for i, subtask in enumerate(subtasks):
            subtask.update({
                "id": self._generate_task_id(),
                "status": "pending",
                "priority": "medium",
                "created_at": datetime.now().isoformat(),
                "dependencies": []
            })
        
        return subtasks
    
    def _create_plan(self, task_description: str) -> SmolToolResult:
        """Create a new plan"""
        try:
            plan_id = self._generate_plan_id()
            subtasks = self._break_down_task(task_description)
            
            plan = {
                "id": plan_id,
                "title": task_description,
                "description": f"Plan for: {task_description}",
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "tasks": subtasks,
                "progress": {
                    "total_tasks": len(subtasks),
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "pending_tasks": len(subtasks)
                }
            }
            
            self._plans[plan_id] = plan
            
            # Format output
            output = f"Created plan '{plan_id}' for: {task_description}\n\n"
            output += "Subtasks:\n"
            for i, task in enumerate(subtasks, 1):
                output += f"{i}. {task['title']} (ID: {task['id']})\n"
                output += f"   Description: {task['description']}\n"
                output += f"   Status: {task['status']}\n\n"
            
            return SmolToolResult(
                output=output,
                success=True,
                artifacts={"plan_id": plan_id, "plan": plan}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to create plan: {str(e)}",
                success=False
            )
    
    def _add_task(self, plan_id: str, title: str, description: str, 
                  priority: str = "medium", estimated_time: str = None,
                  dependencies: str = None) -> SmolToolResult:
        """Add a task to existing plan"""
        try:
            if plan_id not in self._plans:
                return SmolToolResult(
                    error=f"Plan {plan_id} not found",
                    success=False
                )
            
            task_id = self._generate_task_id()
            deps = dependencies.split(",") if dependencies else []
            deps = [dep.strip() for dep in deps if dep.strip()]
            
            new_task = {
                "id": task_id,
                "title": title,
                "description": description,
                "status": "pending",
                "priority": priority,
                "estimated_time": estimated_time,
                "dependencies": deps,
                "created_at": datetime.now().isoformat()
            }
            
            self._plans[plan_id]["tasks"].append(new_task)
            self._plans[plan_id]["progress"]["total_tasks"] += 1
            self._plans[plan_id]["progress"]["pending_tasks"] += 1
            
            return SmolToolResult(
                output=f"Added task '{title}' (ID: {task_id}) to plan {plan_id}",
                success=True,
                artifacts={"task_id": task_id, "task": new_task}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to add task: {str(e)}",
                success=False
            )
    
    def _update_task(self, plan_id: str, task_id: str, update_content: str) -> SmolToolResult:
        """Update a task"""
        try:
            if plan_id not in self._plans:
                return SmolToolResult(
                    error=f"Plan {plan_id} not found",
                    success=False
                )
            
            plan = self._plans[plan_id]
            task = None
            for t in plan["tasks"]:
                if t["id"] == task_id:
                    task = t
                    break
            
            if not task:
                return SmolToolResult(
                    error=f"Task {task_id} not found in plan {plan_id}",
                    success=False
                )
            
            # Add update to task
            if "updates" not in task:
                task["updates"] = []
            
            task["updates"].append({
                "timestamp": datetime.now().isoformat(),
                "content": update_content
            })
            
            return SmolToolResult(
                output=f"Updated task {task_id} in plan {plan_id}",
                success=True,
                artifacts={"task": task}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to update task: {str(e)}",
                success=False
            )
    
    def _complete_task(self, plan_id: str, task_id: str) -> SmolToolResult:
        """Mark a task as completed"""
        try:
            if plan_id not in self._plans:
                return SmolToolResult(
                    error=f"Plan {plan_id} not found",
                    success=False
                )
            
            plan = self._plans[plan_id]
            task = None
            for t in plan["tasks"]:
                if t["id"] == task_id:
                    task = t
                    break
            
            if not task:
                return SmolToolResult(
                    error=f"Task {task_id} not found in plan {plan_id}",
                    success=False
                )
            
            old_status = task["status"]
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            
            # Update progress
            progress = plan["progress"]
            if old_status == "pending":
                progress["pending_tasks"] -= 1
            elif old_status == "in_progress":
                progress["in_progress_tasks"] -= 1
            progress["completed_tasks"] += 1
            
            completion_rate = (progress["completed_tasks"] / progress["total_tasks"]) * 100
            
            return SmolToolResult(
                output=f"Completed task '{task['title']}' (ID: {task_id})\nPlan progress: {completion_rate:.1f}% complete",
                success=True,
                artifacts={"task": task, "progress": progress}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to complete task: {str(e)}",
                success=False
            )
    
    def _get_plan(self, plan_id: str) -> SmolToolResult:
        """Get plan details"""
        try:
            if plan_id not in self._plans:
                return SmolToolResult(
                    error=f"Plan {plan_id} not found",
                    success=False
                )
            
            plan = self._plans[plan_id]
            progress = plan["progress"]
            completion_rate = (progress["completed_tasks"] / progress["total_tasks"]) * 100
            
            output = f"Plan: {plan['title']} (ID: {plan_id})\n"
            output += f"Status: {plan['status']}\n"
            output += f"Created: {plan['created_at']}\n"
            output += f"Progress: {completion_rate:.1f}% complete ({progress['completed_tasks']}/{progress['total_tasks']} tasks)\n\n"
            
            output += "Tasks:\n"
            for task in plan["tasks"]:
                status_icon = "✓" if task["status"] == "completed" else "○" if task["status"] == "pending" else "◐"
                output += f"{status_icon} {task['title']} (ID: {task['id']}) - {task['status']}\n"
                output += f"   {task['description']}\n"
                if task.get("priority") != "medium":
                    output += f"   Priority: {task['priority']}\n"
                if task.get("estimated_time"):
                    output += f"   Estimated time: {task['estimated_time']}\n"
                if task.get("dependencies"):
                    output += f"   Dependencies: {', '.join(task['dependencies'])}\n"
                output += "\n"
            
            return SmolToolResult(
                output=output,
                success=True,
                artifacts={"plan": plan}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to get plan: {str(e)}",
                success=False
            )
    
    def _analyze_task(self, task_description: str) -> SmolToolResult:
        """Analyze a task and provide breakdown suggestions"""
        try:
            subtasks = self._break_down_task(task_description)
            
            output = f"Analysis for task: {task_description}\n\n"
            output += "Suggested breakdown:\n"
            for i, task in enumerate(subtasks, 1):
                output += f"{i}. {task['title']}\n"
                output += f"   Description: {task['description']}\n"
                output += f"   Priority: {task['priority']}\n\n"
            
            output += f"Total estimated subtasks: {len(subtasks)}\n"
            output += "Use 'create_plan' action to create an actual plan from this analysis."
            
            return SmolToolResult(
                output=output,
                success=True,
                artifacts={"suggested_subtasks": subtasks}
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to analyze task: {str(e)}",
                success=False
            )
    
    async def execute(self, action: str, task_description: str = None,
                     plan_id: str = None, task_id: str = None,
                     subtask_title: str = None, subtask_description: str = None,
                     priority: str = "medium", estimated_time: str = None,
                     dependencies: str = None, update_content: str = None,
                     timeout: int = 30, **kwargs) -> SmolToolResult:
        """
        Execute planning action.
        
        Args:
            action (str): Action to perform
            task_description (str): Main task description
            plan_id (str): Plan ID to work with
            task_id (str): Specific task ID
            subtask_title (str): Title for new subtask
            subtask_description (str): Description for new subtask
            priority (str): Priority level
            estimated_time (str): Estimated completion time
            dependencies (str): Task dependencies
            update_content (str): Content for task updates
            timeout (int): Timeout in seconds for planning operations
            
        Returns:
            SmolToolResult: Result of the planning operation
        """
        try:
            if action == "create_plan":
                if not task_description:
                    return SmolToolResult(
                        error="task_description is required for create_plan action",
                        success=False
                    )
                return self._create_plan(task_description)
            
            elif action == "add_task":
                if not all([plan_id, subtask_title, subtask_description]):
                    return SmolToolResult(
                        error="plan_id, subtask_title, and subtask_description are required for add_task action",
                        success=False
                    )
                return self._add_task(plan_id, subtask_title, subtask_description, 
                                    priority, estimated_time, dependencies)
            
            elif action == "update_task":
                if not all([plan_id, task_id, update_content]):
                    return SmolToolResult(
                        error="plan_id, task_id, and update_content are required for update_task action",
                        success=False
                    )
                return self._update_task(plan_id, task_id, update_content)
            
            elif action == "complete_task":
                if not all([plan_id, task_id]):
                    return SmolToolResult(
                        error="plan_id and task_id are required for complete_task action",
                        success=False
                    )
                return self._complete_task(plan_id, task_id)
            
            elif action == "get_plan":
                if not plan_id:
                    return SmolToolResult(
                        error="plan_id is required for get_plan action",
                        success=False
                    )
                return self._get_plan(plan_id)
            
            elif action == "analyze_task":
                if not task_description:
                    return SmolToolResult(
                        error="task_description is required for analyze_task action",
                        success=False
                    )
                return self._analyze_task(task_description)
            
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Planning tool error: {str(e)}",
                success=False
            )