import streamlit as st
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt
from collections import Counter
import os

# Initialize OpenAI client (Replace with your API key)
client = OpenAI(api_key="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")

def get_tags(subject, description):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class professional support ticket analyser.\n\nYou will be given a text dump. It is a support ticket. \n\nThe ticket will have the title, description and an image file optionally. \n\nYou need to understand the ticket and provide me with the right set of tags as a list. If the image is present, analyse whether it is an SDK image (true if the footer of the image says \"powered by HyperVerge\"). \n\nThe output should always be a JSON with the key \"tags\" which is a list of tags. The list should not be empty.\n\nOnly one or more of the following should be present in the list of tags. Accept any case-sensitive.\n1. websdk - when the text or image contains \"websdk\", \"web journey\" or the image has a footer \"powered by HyperVerge\"\n2. selfie module - when the text or image contains \"selfie tips\", \"remove spectacles, hats, and masks\", \"proceed to take selfie\", \"take a selfie\", \"please look straight\", \"place your face inside the circle\" or \"stay still and capture now\" \n3. document module - when the text or image contains \"pan card\", \"aadhaar card\", \"voter id\", \"let's verify your identity\", \"ID card\", \"Government ID card\", \"Proceed to capture ID\", \"document is without any glare and is fully inside\", \"lighting is good and letters are clearly visible\"\n4. video statement - when the text or image contains \"read each digit out loud\", \"start recording\", or \"rec\"\n5. countries module\n6. barcode module - when the text or image contains \"scan qr\" or \"qr code\" or \"place qr inside the box\" or \n7. form module - when the image has \"text box\", \"drop down\", \"check box\", or \"date picker\" vertically stacked in any order\n8. nominee module - when the text or image contains \"add a nominee\" or \"skip nominee details\"\n9. wet signature module - when the text or image contains \"add your signature\", \"draw signature\", \"upload signature\", \"guidelines for signature\", \"sign here\", or \"draw signature on screen\"\n10. bank account verification module\n11. otp module\n12. email module\n13. digilocker module -  When the text or image contains \"digilocker\" or \"accounts.digilocker.gov.in\"\n14. income validation module -  When the text or image contains \"income verification\", \"bank statement with OTP\", \"fetch bank statement via account aggregator\", \"finvu\", or \"waiting for account aggregator\"\n15. camera module - when the text or image contains \"please look straight\", \"place your face inside the circle\", \"stay still and capture now\", \"remain within the circle\", \"without any glare and is fully inside\", or \"lighting is good and letters are clearly visible\"\n16. blur\n17. recording\n18. browser permission - When the text or image has \"allow permissions\"\n19. file size limit\n20. domain whitelisting\n21. linkkyc - When the image or text containing \"link-kyc\", you can tag it a linkkyc\n22. Application review - When the image or text containing \"kyc status\"\n\nIf you are not sure or the input doesn't match any of the criteria return the empty list.\n\nAnalyse the input and share your reasoning before arriving at your answer.\n\nSample 1:\n```Input\nTitle: Uni <> Hyperverge || Cropped Selfie Issue\nDescription:\nHi Team,\nCurrently, the images that we are getting post Liveliness checks are quite cropped.\nIn most of the cases we noticed that the bottom part of the face gets completely cropped out.\nRather, we want to utilize the complete selfie captured rather than the cropped image.\nCan you please help out with this?\nRegards\nShreyansh\n```\n\nOutput: {'tags': ['selfie capture']}\n\nSample 2:\n```Input\nTitle: [content bypassed security scans] RE: Observations raised\nDescription:\nHi Team,\nThank you for your time on the call today. \nAs discussed during the call, the resolution for the Cross-site Scripting issue is scheduled to be released by Wednesday EOD. A new SDK version will be provided, which will require an upgrade on your end.\nWe will keep you informed about further updates.\nRegards,\nNivedha M\nHyperVerge Support Team\n```\n\nOutput: {'tags': ['security', 'sdk']}\n\nSample 3:\n```Input\nTitle: Failures in Selfie integration - PayUfin\nDescription:\nHi team,\nWe are facing unexpected errors in the selfie integration.\nExample of one of the user - Issue faced twice while attempting hyperverge selfie. The transaction was successful in third attempt. Can you please check why it was failed twice?\nTransaction id = 32517116-1737529739721\nThis issue is occurring for a high number of users hence impacting 7% of the funnel. Please help urgently.\nThanks\n```\nOutput: {'tags': ['selfie capture']}"
                },
                {
                    "role": "user",
                    "content": f"```\nInput\nTitle: {subject}\nDescription:\n{description}\n```"
                }],
            response_format={"type": "json_object"},
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        # Correct way to access response content
        if response.choices and len(response.choices) > 0:
            tags_data = response.choices[0].message.content  # This should already be JSON
            return tags_data  # Expecting {'tags': [...]}

        return {"tags": []}  # Return empty list if no response is found 
           
        # tags = response["choices"][0]["message"]["content"]
        # print("Generated Tags:", tags)  # Print tags
        # return tags  # Expected format: {'tags': ['tag1', 'tag2', ...]}
    
    except Exception as e:
        st.error(f"Error fetching tags: {e}")
        return {'tags': []}

def plot_tags_distribution(tags_list):
    """Function to visualize the tag distribution."""
    all_tags = ', '.join(f'"{tag}"' for tag in tags_list)
    # Split the tags string by ', ' and strip any extra spaces or quotes
    tag_list = [tag.strip('"') for tag in all_tags.split(', ')]

    # Count occurrences of each tag
    tag_counts = Counter(tag_list)
    
    # Print tag counts
    print(tag_counts)
    if not tag_counts:
        st.write("No tags found to visualize.")
        return

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(tag_counts.keys(), tag_counts.values(), color='skyblue')

    # Labels & title
    ax.set_xlabel("Tags", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Distribution of Tags", fontsize=14)
    ax.tick_params(axis='x', rotation=45)

    # Show chart in Streamlit
    st.pyplot(fig)

def main():
    st.title("Support Ticket Analyzer")
    
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Ensure necessary columns exist
        if "Subject" in df.columns and "Description" in df.columns:
            st.write("### Processing Data...")

            # Apply function to each row
            df["tags"] = df.apply(lambda row: get_tags(row["Subject"], row["Description Text"]), axis=1)

            st.write("### Updated Data with Tags:")

            st.dataframe(df[["tags", "Subject", "Description Text"]], use_container_width=True)

            # Visualize the distribution of tags
            st.write("### Tag Frequency Visualization")
            plot_tags_distribution(df["tags"].tolist())
        else:
            st.error("CSV must contain 'Subject' and 'Description' columns.")

if __name__ == "__main__":
    main()