# Introduction
![](architecture.png)
The repo consists of four aws lambdas, and the architecture graph above shows how they interact with each other.

The lambdas compose the heart of the system. They mainly contribute to two features:
  - judge the users' status by their photos and screenshots
  - extract discussion topics and incorporate them with replies

The deployments are a bit tricky, please refer to the following sections to find how to deploy each lambda and what they exactly did.

# focus_judger

# record_handler

# topic_extractor

# reply_catcher