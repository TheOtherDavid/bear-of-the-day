# bear-of-the-day
This is a program that will construct an image prompt by randomly combining items from a list of styles and a list of scenes, call the OpenAI DALL-E 3 API, and then send the image in an email to the chosen recipients.
And the pictures are of bears, because bears are cute.

## Technical Details

The program is implemented in Python and uses the following key technologies:

- **OpenAI DALL-E 3 API**: This API is used to generate images of bears based on the constructed prompts.

- **AWS CloudFormation**: The infrastructure of the program is defined and managed using AWS CloudFormation. This includes the deployment of the AWS Lambda function.

- **AWS Lambda**: The core logic of the program is implemented in a serverless AWS Lambda function. This function is triggered on a schedule, constructs the image prompt, calls the DALL-E 3 API, and sends the email.

- **SMTP via Gmail**: The program uses SMTP via Gmail to send the generated bear image to the chosen recipients.

## Setup and Deployment

The program is packaged and deployed using the AWS Serverless Application Model (SAM) CLI. The `sam package` and `sam deploy` commands are used to package the application and deploy it to AWS, respectively.

Please ensure that you have the necessary AWS permissions and that your AWS credentials are correctly set up before deploying the program.

Ensure that you have set up the necessary environment variables (`SENDER_EMAIL` and `SENDER_PASS`) for the Gmail account used to send emails.

## Usage

Once deployed, the program will automatically run on the defined schedule. You can customize the list of styles, scenes, and email recipients by modifying the corresponding variables in the Lambda function code.
