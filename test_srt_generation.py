from src.videoTools.video import VideoTools

# Sample word data from the user's input
words_data = [{'word': 'So', 'start': 0.0, 'end': 0.30000001192092896}, {'word': 'me', 'start': 0.30000001192092896, 'end': 0.5199999809265137}, {'word': '20F', 'start': 0.7599999904632568, 'end': 1.2599999904632568}, {'word': 'and', 'start': 1.4800000190734863, 'end': 1.659999966621399}, {'word': 'my', 'start': 1.659999966621399, 'end': 1.8200000524520874}, {'word': 'boyfriend', 'start': 1.8200000524520874, 'end': 2.2200000286102295}, {'word': '24M', 'start': 2.4000000953674316, 'end': 3.0399999618530273}, {'word': 'have', 'start': 3.319999933242798, 'end': 3.440000057220459}, {'word': 'been',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          'start': 3.440000057220459, 'end': 3.5399999618530273}, {'word': 'together', 'start': 3.5399999618530273, 'end': 3.859999895095825}, {'word': 'for', 'start': 3.859999895095825, 'end': 4.059999942779541}, {'word': 'almost', 'start': 4.059999942779541, 'end': 4.340000152587891}, {'word': '2', 'start': 4.340000152587891, 'end': 4.579999923706055}, {'word': 'years', 'start': 4.579999923706055, 'end': 4.840000152587891}, {'word': 'and', 'start': 4.840000152587891, 'end': 5.0}, {'word': 'live', 'start': 5.0, 'end': 5.139999866485596}, {'word': 'together', 'start': 5.139999866485596, 'end': 5.480000019073486}]

# Create an instance of VideoTools
video_tools = VideoTools()

# Generate SRT file using the provided words data
# We'll pass an empty string as file_path since we're providing the words directly
srt_file_path = video_tools.generate_srt("", words=words_data)

print(f"SRT file generated at: {srt_file_path}")
