from typing import Optional, Dict, Any
from app.schemas.email import EmailTemplate, UserEmailContext
from app.utils.ai import client

DEFAULT_STYLES = {
    "colors": {
        "primary": "#0052CC",
        "secondary": "#0747A6",
        "accent": "#4C9AFF",
        "background": "#FFFFFF",
        "text": "#172B4D"
    },
    "fonts": {
        "primary": "Arial, sans-serif",
        "secondary": "Helvetica, sans-serif"
    }
}

def generate_email_content(
    template: EmailTemplate,
    user_context: Optional[UserEmailContext] = None,
    content_variables: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate email HTML content using AI based on template and context
    """
    # Merge default styles with custom styles
    styles = {
        **DEFAULT_STYLES,
        **(template.style or {})
    }
    
    # Prepare context for AI
    context = {
        "template_type": template.type,
        "user_context": user_context.dict() if user_context else {},
        "content_variables": content_variables or {},
        "styles": styles
    }
    
    # Generate system prompt
    system_prompt = f"""
    You are an expert email template designer. Create a responsive HTML email template following these requirements:
    
    STYLE GUIDELINES:
    - Use these colors: {styles['colors']}
    - Use these fonts: {styles['fonts']}
    - Make the email responsive and mobile-friendly
    - Use proper HTML email best practices
    - Include proper spacing and padding
    - Optimize for email clients
    
    EMAIL TYPE: {template.type}
    USER CONTEXT: {context['user_context']}
    CONTENT VARIABLES: {context['content_variables']}
    
    CUSTOM PROMPT: {template.prompt}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate the HTML email template."}
            ],
            model="qwen/qwen3-32b",
            temperature=0.7,
            max_completion_tokens=2048
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating email content: {str(e)}")
        return None

def get_template_prompt(email_type: str) -> str:
    """
    Get default prompts for different email types
    """
    prompts = {
        "marketing": """
        Create a compelling marketing email that:
        - Has an attention-grabbing header
        - Includes product highlights or featured content
        - Has clear call-to-action buttons
        - Maintains brand consistency
        """,
        "welcome": """
        Create a warm welcome email that:
        - Personally greets the new user
        - Highlights key features or benefits
        - Includes next steps or getting started guide
        - Provides support contact information
        """,
        "order_confirmation": """
        Create an order confirmation email that:
        - Thanks the customer for their purchase
        - Lists order details clearly
        - Provides tracking information if available
        - Includes customer support contact
        """,
        "promotion": """
        Create a promotional email that:
        - Highlights the special offer clearly
        - Creates urgency with time-limited deals
        - Shows product benefits
        - Has prominent call-to-action buttons
        """
    }
    
    return prompts.get(email_type, "")
