to the A
OK, so this is where I.
Struggle a little bit with this process, right? Because in my mind, this is worth probably us spending a good 20 minutes sort of manually cleaning this up just to make sure that it reflects the way that we're thinking about the system. So as.
As an example, if I go through um um.
Activity framework. So at the very almost at the top activity framework. So key components, generic activity, template system, activity, states, draft, published, active, expired activity, specific metadata and configuration.
Etcetera, etcetera. I think to me it's almost like some of that belongs and I'm thinking out loud, but some of that belongs in a.
It's almost like this is how we want to think about the logical data model for the application, right? So almost like the mirror diagram. I don't know how we would go from this to having something that resembles the mirror diagram that you were working on. OK, So what I would do, let me experiment, because we can always undo it.
Right. Yeah, I'm gonna go to the Miro diagram.
And I'm wondering if the mirror diagram should have been one more piece of content that we fed into this. Yeah, it's not too late. I can totally do it. So like.
I was gonna say like configured activities.
And then like admin starts or opens session.
and uh and this one is admin defines activities.
Configured activities admin opens the session and then I'll say I'll say session start.
And then like so this is like admin oriented. I'm just like I'm kind of riffing and this is participants oriented. So purple for participants, participants.
Connect to session via QR code.
And reverse that.
And then.
Uh.
Users play or participate. Sorry, participants participate in pointing poker and I'll just copy that for everything.
Participants participate in pandering and then like last activity ends view.
Proceeds to summary. I don't know. Well, and then that's the like it's blue for some reason. I don't know why. So I'm just going to like, see what happens if I take a picture of this diagram.
And.
We have a concept of a concept of users or admin users defining sessions with a configured order of activities.
Once the admin opens the session, we get a viewer we can share on a screen showing a QR code that users can scan with their phone.
To join the game and enter a nickname for themselves, they proceed through the activities.
And at the end there's and after the final activity there's a summary. Here's a high level diagram and I'll paste the image which I can see is there. So I'll hit enter.
And we'll see how it evolves. Yeah, because you haven't asked it to do anything with that information. I don't care. It'll figure it out. It'll know. It'll figure out to update Gaja features. Let me add this flow information to our features documentation to provide better context for the user journey.
There it is. We have a high level. That was the only changes it really made. Ohh Let me also update the session management feature to better reflect the specific flow shown in your diagram. Nice. Good.
So I I was thinking that the out regenerated features, but really at the end of the development cycle, the cross device and synchronizations that I believe is one of the key features that we are trying to.
Yeah, it's not. I don't think it's in an order of priority right now. Yeah. Yeah, agreed. I think we're hoping we'll be able to like, like, OK, now it's time to go create the issues, create the issues in the order of of like in the order such that they can be that they don't block each other.
Other like like do the most foundational ones first or something, yeah.
I was confused because it separated in phases. So it at the last. Oh, at the end. Oh yeah, yeah, at the end. You're right. At the end, it says feature feature prioritization notes.
I would also want I want the intro screen for the session to have the QR code nice and big, but I'd like for the QR code to be there for participants to join later if they showed up late. Always show the onboarding thing and let users tend to let users join halfway through or part.
Way through so once it's done, but it's always making a series of tweaks.
Core functionality for creating, managing and running events with ordered activity sequences, session lifecycle management, ordered activity sequence, configuration, execution, QR code generation for participant joining, participant nickname registration and management, automatic progression through activity sequence.
I would say optionally automatic and we can we can humanly tweak these two.
I can create a session and define the order of activities. I can open a session to make it available for participants. As a participant, I can scan a QR code to join an active session. I can enter a nickname when joining a session. I can display session information and QR codes on a shared screen.
One of the things that I think is interesting to think about in terms of.
Applying. So a couple of things to think about in terms of applying this at scale, right? Right now, the only way that we've leveraged the fact that we're four people working on this is discussion, which is not bad, right? But for we haven't yet gotten to a step where.
I'm gonna go do something. You're gonna go do something, right? Right. We're gonna go independently, do do things. So that's one thing to think about. Probably a step that we should get to soon. Yeah, I agree. Another thing to think about is.
In terms of how much, how much?
Editing. Do we wanna go through here versus, hey, let's just create the system and see what it does. Yeah, right. And then go from there. Because the cost between the two different things may not be. We could spend a bunch of time trying to say, you know what features 7.
9 and 12 we don't actually need versus hey, just go build them and we'll review them and we'll see. Maybe we'll like them the way that they are. And that brings me to the last thing that I'm thinking about, which is the thing that we really struggle with in a lot of orgs that we work with is.
Requirements traceability throughout the different steps, stages of the development process, right? And I think the fact that this is being generated is a way that we can really say, hey, these sets of users cuz we have user story skeletons here, all of these user stories.
Are in relation to this particular feature and we can keep that traceability alive all the way through the implementation, right? And so that may be a way that we can say.
What? What? That's a great UX improvement. Damn right it is. Yeah, that's sick of fancy. And so that could be a way that we can say, hey, yeah, let's just go ahead and create all of these features initially. So I agree.
The thing I think that's missing right now is that we've been very light in terms of our technical guidance. But now we've done a really good job of gathering what this application should do. But we didn't even give it a foundation. Like we said, use Python. It's gonna be some bad ****. I think we did because if I look at app explicitly.
Can I weigh in on that real clip you just brought up? I really like this thing here that you had like the the the had like phases. Yeah, the development cycle, which is cool. We didn't have those. I know you probably didn't because that does that all the time. Add a phase in front of that which is like like bootstrapping the application and I said those things as like like.
Define the tech stack even, right. And like, yeah, build the hello world thing. That's what we are. I think we are, we're just if you because you're just joining us. So left side of Pam, yeah, defining our pipeline going from requirements to features, we're just, we're right here.
I think we're about to be able to generate our user stories and I think one thing that we can do in parallel is as that's being generated and reviewed, then we can work on basically our what we call Sprint 0 activities, which is hey, let's now decide on.
What a tech stack is gonna be and do that bootstrapping. The moment in time I wanna get at and this is relevant to Tristan in essence specifically. This planning's high level, but this is a reasonable level of planning for us to be doing for this kind of project and you can conceptualize it and you didn't need to go detailed yet, but as you go detailed you need to.
Increment through each of those sections. So it's not too much context and you're not just like going back and checking. We talked about that. Yeah, you probably already know that. But the take away that I give to people most of the time in coaching that they don't get is they think about like a plan like this and they're like maybe I have a parent, maybe I have a child or they have a plan and now it's tickets. And for me, whatever it is, it's like it's an.
The infinite number of children plans as needed to achieve an outcome. And right now you've got your highest level, which is like the totality of the app. The next piece might be like, here's the workshop, we're gonna bite off this phase and this phase, for example, and you got a new plan and it doesn't necessarily even need to be the one that goes highly technical. Just do it to where it feels right for the moment you're trying to do.
And then you might build a child off of that and you might build a child off of that and you might have decided like and that's a that's a good point because I think one of the things and I think I'm guilty of this right now. I'm still in the mindset of eventually this needs to be user stories, right? Exactly.
The user story does not necessarily need to be the work item that encapsulates the last level of detail for the requirements, right? It could be something else. But yeah, right now we're still thinking what we wanna get to is a set of user stories. Yeah, so plans can look different and you can use them for a lot of different activities. All they are is a set of instructions that you can.
User agent across many sessions and store those facts and come back to them later. Yeah, because a lot of people, I think that anti patterns, they get too stuck on like what a plan should or shouldn't be and what level of detail it should or shouldn't be. The answer is like whatever's right ******* in front of me that makes sense that I want to codify, right? Sometimes it's functional, sometimes it's highly.
So play with that I guess as you're going through these next phases, cuz it's I think like the crux of one of the harder things to help teams through. So those are two. There's two things that we haven't done yet that I think I would say need to be done before we crank out a single line of code here. And one is we haven't even defined.
The rules. None of this is gonna persist if I create a new session. I'll have the documents. I'm sure it'll do a good job of finding it, but we should create the dot GitHub copilot dot MD file that says this is where we defined our goals. This is where we defined the features of our application.
Then I also separately think we need to define. Don't just say Python for the back end, say like Python with fast API. Don't just say React, but give it some guidance about how to build the front end. Yeah, and maybe don't say Ajax as well. Yeah, yeah, I don't know. I see that it says Ajax. I'm just like, I'm going to delete.
I get the crap out of that. So I do this. I handle this two ways in my workflow. This is useful. So yes, you just finished a lot of things and there's takeaways from this chat that can turn into rules so you can finish the chat with. Now let's make some rules that are relevant. One thing that I often do either in the chat or at the end right now is you just brought up a few different things that you thought about while you were doing this. You might say like.
But just.
Let's build a plan to do the rule system. Now take this chat. We want a plan that's only about rules, and let's codify that plan too. So sometimes it's useful to put like your infringement activities down as separate. Yeah, I like that. Yeah. And just work those when you're conceptually ready to work them in their own session and their own chat. Because you might want to just close this chat down. Yeah, do a new one and say now we're gonna work that.
To build the rules from the insights that we gain, and we're also gonna add a bunch of context by searching the web for best practice on like how to build the rule systems. You don't want the rest of the happen here taking up your space and confusing the agent that's trying to work through that other.
Yeah, yeah, that's right. Then the third thing is, I'm assuming as part of this, we should probably have some thought to a pipeline to deploy this thing. Because, I mean, we can't scan a barcode and get connected to an app that's hosted on local host, right? Like it's it's got to be.
It's got to be deployed somewhere. I mean, but yeah, yeah, I mean, thank you. Yeah. And you have GitHub Actions. Yes. OK.
Shoot. Well, OK. So all good. Yep, I think so. I'm just checking in around around the camps. Yeah. Thank you. Enjoy.
So, So what you're about to ask is a little bit different from what we just talked about with Landon, right? Oh, shoot. And in what way? So, so there's a bunch of context here. Yeah, that's been useful to generate what's been generated. So basically the context right now.
Is split in two different things. One is the artifacts that we've created and the other one are the actual chat session that we just had, right? And so now we're saying we want to transition from, we want to keep these artifacts, that's persistent. OK, OK. And now we want to transition in this chat session.
From having a chat session that was geared towards generating the artifacts to now having a chat session that's gonna gear towards generating the GitHub rules, right? Yes. So what Landon suggested, which I think is great, is.
Now, using the chat session context, come up with a plan to generate the complex rules, right? And then we'll start another session that says, OK, so this is not a new session, use that, execute that plan.
To to generate the rules. Does that make sense? I think so versus generating the rules here, which is I thought that's what you were about to do. OK, OK, that's probably what I was about to do. So like, what's like what prompt am I giving it now then? First of all, let's commit those. Oh yeah, yeah, good call. Let's sync first because I pushed to get ignore file.
OK.
Thank you for that.
All right, that's up. OK, now what? Cool. So now we want to say, come up with a plan.
To translate this discussion into a set of.
GitHub rules, GitHub copilot rules.
OK, ready. Let's see what that here we go.
Probably. Uh, yeah, goals is good.
OK, while this is happening, let's have a conversation around our tech stack. Do we want to pause the meeting here and put a break in or do we want to? It's fine.
Uh, so we're saying front end is react. Mm-hmm. Anything special about it? Tan stack? Sure. Why not? I don't know. Server components.
What's that? That means we don't need a back end. Ew.
I hate it. So I think we need we need to balance. I know where you're going, which is I think you just want to be as simple as possible and as lightly as possible. And I think for the purpose of this exercise, we may want to make the application a little bit more complex than it would otherwise be.
Just to kind of reflect a little bit more what our client environments might be. That's what I said. I just said you. But are you a React guy? I'm not a React guy. OK, are you a React guy?
I know I do. What's that? I know enough to muddle along. OK, what's your Do you have a front end preference? I'm more familiar with Angular. OK, are you more familiar with Angular as well? At this point I believe I'm more familiar with React now.
OK, OK, React seems like the way to go. Like Angular is pretty heavy in comparison and these are supposed to all be like either one of you two is going to be opinionated on specific React components that we want to use and we can.
Do that and reflect that opinion here. Or we can just go out and ask Copilot for recommendations on best practices for React front end development that we wanna have reflected in the GitHub Copilot rules. We do have to be careful though, and I'll say this for the benefit of the transcription.
that like GitHub or all of these LLMs can tend toward like the create React app, which was deprecated. So we have to like like don't do that, but I guess hopefully TanStacks got a thing for it. Use TanStack to create the initial React application.
OK. OK. What did it do? OK, does that give us, does that give us a set of React components as well? That includes stat CN, yes. OK.
OK, all right. And then on the Python side, are you gonna be your Python opinionated? I am very fast API. And what else do you have? Like a testing? Same for React. We have a like a unit testing library that we wanted to use and.
Can stack included unit testing? I'm not sure. I'm only familiar with Jess.
From Jasmine, yeah.
Oh, look at that. That's cool.
So it gave us the plan as an artifact, which is cool, and it says it's going to create the instructions.md file that will link over to the other files for architecture, personas, activities, and tech stack.
And then instructions, tech stack rules. This is the architecture rules that'll put into phase two and ohh session activity.
Participant joined at last activity. Oh, that's interesting. So that's kind of a data model ish. OK, user experience rules, so I don't think we would want our.
Data model and the rules. That makes sense. What is this part of? It's part of architecture rules.
Still not that rules are more meta. True that they are. Yeah, true. True that they're more meta. I I mean, like, I kind of.
Because I do like it. I like that it's spelling out that we have the concept of sessions, activities and participants like those are good.
The individual properties of the of the models or perhaps to do what? Like I like that it's calling out that we have a session activity and participant model. I don't need to know the individual properties necessarily, although it is kind of neatly laying out the expectation is that as we expand and have more activity.
Types that we would come back and add this to the enum of types, but.
I don't know, kind of say let's go with it for now. User experience rules got the different personas. Viewer runner persona. Nice, you can capture that.
I'm sorry, I'm going so fast you can't even read it.
2.
Or.
Oh.
Cool.
3.
Yeah, I mean that looks, that looks pretty good. And then he's got the tech stack as well. I think we can make some updates. So why don't you accept that and then we'll start catching it up. That's last API support one second.
Probably. I don't know. It's a good question.
Oh yeah, it already says fast API. I love it. Nice work guys. I didn't know where it got that. It's like it's like when suddenly Facebook starts handing you ads or something that you're like, I didn't remember telling you anything about that.
This is kind of stack or yes, OK.
OK, so in this so start planning implementing any specific part of this plan, such as creating the initial copilot instructions. That's right, create all the dot. It's not happening at this.
Called out in this plan. It's like non. It's so constant. It doesn't seem real. Like it might be an average or something, right? Well, yeah, it's, yeah, it's some. The total should be real. Yeah, yeah, the total, I'm sure is real. So shouldn't be like a live.
Actual counter, right? 10 million per hour just count something. Yeah, yeah, yeah, yeah, right. Something like that. OK. I'm sorry, did you want to modify this plan or do you want we'll modify it together in PR?
Yeah, I think mostly it's the tech stack piece of it. OK, I think we need to pay attention to. I stop that then and I don't think it actually gave me any copilot files yet, so I'm gonna delete that.
And so that's what we got. Get status. Actually here what I'll do is I'll start using this thing. Stage that and we'll give me a nice auto generated commit comment. Let Copilot rules implementation plan. Ha chow.
OK, I should have not committed that to main again. Gosh darn it. OK, also, we don't have permission to push to main like you do really losers.
OK, so that's fair. I will let's establish our first rule. Create a copilot rule. Oh wait, this might be a good time to integrate the MCP.
Integrate the GitHub MCP into this solution.
Do you integrate it into a solution or into your?
I'm always integrated into my header from CP. Yeah, well, we'll see what happens.
Mm-hmm. So that's go back to your files. I think that's what's gonna create your initial compiled file, compiled for better put the first file in it.
Yes, I thought there was a VS code specific file that integrated with MCP, but there is there's you can set up the MCP servers in VS code. Yeah, I think I thought so. That's what I was trying to get it to do.
Yeah, yeah. What is it doing now? Oh God, what am I? It's building your rules file. It didn't ask for that. I know what I did wrong. Hang on. Sorry. All right. I I asked for that and then I canceled it. And then let me just restore that checkpoint.
Yes. OK, they're gone. They're gone. They're not gone. They're working on it.
Okay, I'll just delete them. Deleted.
I'm going to open a new session. Let's integrate this VS Code project with the GitHub.
MCP.
Yeah.
3.
Yeah, make it so.
I have no idea what I'm doing with my architecture or anything. That's great. It's exactly what I want. I already get ignore. What'd you give me? It's a default. Actually, no, I just test to give you a default. OK, that's nice of you. It's nice of the LLM.
OK.
It should not care about any of this to set up MCP. I wouldn't think so either, but that's OK. I'm gonna let it go.
This is the about the Kaha live engagement product. Oh, does it go into package dot Jason? There's no, there's no NPM I know.
Why would we have a package ID? Oh, 'cause eventually we're gonna get a test.
Don't know.
Is he gonna write an MC pizza? Better not. No, I said the GitHub one.
GitHub MCP. Let me set up a GitHub MCP integration with creating the necessary config files.
K and and it's pulling in the mall context profile protocol SDK.
It's like a REST API server.
Oh gosh, really? Zod is like a um.
Um.
Data validation library.
Yeah, no. Now let me create the MCP server implementation. I'm not gaffing. No, you stop. That's naughty. Okay. All right. It is ready to go.
Cancel that. Oops. Oh, sorry. That's gone. That essentially did the same thing. OK, I'm happy that it got rid of it. We'll figure that out later. OK, where were we going next? Because what did I want?
I forgot what I want. I wanted the MCP server. Yeah, we want. We're trying to create our rule. Oh, I wanted to create a branching rule, but OK, that's fine. We'll figure that out later. OK, so.
Why don't we, why don't we put that so so we're refining the tech stack to the thing that I was saying earlier. So far we haven't, we've been very single threaded, right? But we have multiple people.
So Mauricio.
Joe Tristan.
And.
So, Tristan, do you wanna put on your list that you're gonna do MCP once? Yeah, you can just do things without us looking over your shoulder. Sure. OK, so let's just start handing things out maybe. OK, so we've got.
So it it brings up a good point about the database. We are going to need a database to hold this even if it's just a temporary one like an in memory database or Postgres database like those would probably be fine. Do we want to select the cloud?
Yeah, I think it's time. I mean, I would prefer AWS, but I don't care that much. You're on AWS if you're volunteering to do the AWS stuff. Well, I'm definitely volunteering to do the Python stuff, but like I I I don't want to volunteer to do the Python stuff.
And the MCP and the platform. But I could. What MCP stuff are we saying we need? So this is for when we get to eventually the stories, taking the features and the goals and turning them into stories like I want. That's totally a thing that Copilot will easily do. So are we storing all the stories and stuff in?
Hub or OK, yeah, 'cause otherwise we could create like a Jira MC or integrate with a Jira MCP server, but then we'd have to get Jira and it's boring.
So, OK, well, let's go. Let's refine the tech stack then. So let's we've got one of these. Is it show chats? Nope. I thought there was a way to go back to a previous chat, but Oh well, it's fine.
Go pilot rules plan. OK, so.
OK.
For the tech stack, we'll deploy this solution onto AWS. Um We need a data persistence solution, but it doesn't have to be fancy.
It could. Do we have like a presumption? What do you choose? You own this one. I'd vote for SQLite. SQLite, OK.
Uh.
Within AWS, OK, I'll just say it is.
SQLite. Does AWS have a SQLite? SQLite. SQLite is usually in process, so it's part of your app. OK, OK, so in memory, yeah.
So how does that deal with multiple? Well, then do we want multiple? Oh yeah. Oh, OK. Oh, SQLites, no. OK, good. Yeah, I'm glad we talked about that. But we can do just like an AWS data service like a.
Oh yeah, like RDS. Yeah, yeah, maybe not. But do we want a relational database or? Yes, we want a relational database. Yeah, OK, we don't have to, but that's fine. It seems like a fine thing to have in the. I'll say not Dynamo. The thing I like about it.
Is that I mean, like I know we could do with all the user inputs coming in. So there's some probably going to be some kind of concept of transactional locking and yeah, like week one, but yeah, maybe. OK, well, I'll let you. OK, so RDS.
Yep, uh uh, we'll use Python.
With a fast API for the back end tested with high tests. Yeah, that's a good question. Who wants to work on this? Who actually wants to work on the platform in deployed how in AWS?
GitHub actions. Yeah, as as functions or yeah, is is it? Can we get away with functions? Probably if the database is separate.
Yeah, well, do we want microservices or no? Or are we doing web sockets? We could just simplify it with long polling. Yeah. Oh, that's. It is ugly. But yeah, OK, well, yeah, let's.
They are. What do we need? Well, we just need to store something in. So let's let's just talk about this for a second. So what do we need? What would we need a persistent connection for? We want to here's. I'm the server I've.
Opened up a session. The way that clients connect to that session is they just scan like your code, right? So now they have a client and their client needs to know.
When I'm moving from one activity to the next, right? So that's and receive the user's input. That's the persistent. Yes, yeah, exactly. And if right to go from one activity to the next, I could conceive of some activities driving a state change from the viewer.
Like, like reset points, you know, on on playing poker or or or move on to the next story, right? Yes. Yeah, all of that. Just regular pulling. Yeah, yeah, well, pulling.
Well, I'm saying it's like the server doesn't actually need to push. Our stuff isn't like super real time. It's delayed by it just pulls the server every couple seconds. That's yes sufficient. So but the yes, I I agree. I think we could start with polling and then if we have time we could refactor it to a websocket solution as a.
Uh, enhancement. Use our kiss principles to the Yeah, yeah, exactly. Um.
OK, uh.
Do we have what do we have to do? Like CDK or something to get these deployed through GitHub actions?
Uh, or well, we didn't. So on where we're deploying to, are we deploying to the lambdas or are we deploying to? I think, I think lambdas. Lambdas. Yeah, that are getting pulled every two seconds. Yeah, why?
What else are you going to use lambas for?
Does that sound like a good use case for lambdas? OK, OK, it's not high memory and it's not long last. Alternatively, we could build like a containerized application, but then we're saying for the database we're using RDS. So we have all these lambdas flying around. Yeah, well, maybe not all these lambdas flying around.
But just, OK, so Lambdas as potentially a foundation for microservices, but we have centralized storage, so we're not doing microservices, but we have these.
You know, ephemeral services that are all just gonna connect to the same data store? Yes. OK, yeah, it's a bit of a.
Yeah, it could be. But yeah, I mean, it's going to be fast API, so it's going to be a hosted API solution anyway. Like if we could run it as an application, then it would respond to. What do you mean it's going to be a hosted API? Like fast API is a thing, is a CLI. You can just run the thing and it'll like listen to all the.
Like it could just simply be an app as opposed to deployed as a Lambda, right? But you're not gonna deploy. It would be weird to deploy fast API instance as a Lambda. Yeah, that has to be brought up and down every time any of the any of the its API endpoints are.
So I think what I'm suggesting is deploying it like and I'm not a container expert, but if we could run an A hosted A containerized application, yeah, so a bean stop or whatever on what's what's the AWS container service? No, just ECS ECS do a container.
Yeah, ECS. Yeah, yeah, that would make sense. OK, we've decided we're using ECS. We need public IP.
We need a public IP. Give us that. You're not. What are you doing? I'm talking to the transcript. I know, but we're are we running this transcript through here? Probably not because we're we're doing it incrementally, right? That's right. Yeah. Yeah. So I have to do that.
I haven't done it yet. OK, OK, some sort of ECS will be public IP address for it.
And is there like what are you trying to ask here? Right now I'm just trying to give it high level guidance to fill out the final version of the copilot rules plan. We still haven't built the copilot rules. Yeah, so yeah, but then I wanna ingest the new transcript. It's OK. I just wanna acknowledge that I think we're mixing our metaphors a little bit.
To me, the copilot rules are meta about how we want you to go about doing the work, and then we define what the work is in specific prompts that are for that work. But here we're doing both. So for example for this, what I would have naturally said in the copilot rules is.
We want the infra required for this to be set up in AWS using Terraform as an example, right? That's the rule. Anytime you want to create some infra, anytime you want to do any platform engineering work, use Terraform for that and set up for example and set up AWS as your target platform.
Yeah, right. Yeah. And then we're gonna have, and then one of us is gonna take on the job of doing the deployment stuff and actually go and execute on that, right? Does that make sense? It does. Yeah. So you've documented some details here, so we might as well just capture them. I see. Yeah, I'm gonna hit go on this.
Well, the front end back end is to be deployed to Amazon ECS. I don't know where the front end happens, but it's Amazon hosted React front end as well. Yeah, on S3.
Yeah, the CloudFront stuff. Yeah, and all all infra work should be in Terraform. Infra work should be Terraform or I've never done Terraform.
Is that better than cloud formation? It's just not AWS specific for Sam. Oh, OK, Terraform. I love it. OK, so I'm going to hit go on that. I'm going to go get the new transcript and have that be ingested as well. Then we can create copilot rules, which we haven't done. Then we can go off on our separate directions.
OK, OK, then the copilot rule should give us like they're not just meta, like it functionally drives the approach for us, which should be good, like consistent across multiple sessions.
OK, you. Yeah, as you're doing that. So Tristan owns MCP.
I am not a AWS expert, but I don't. I wouldn't mind actually diving into that a little bit. OK, so I can take, I can take platform engineering. Awesome. Who wants the front end and who wants the back end?
Preference. I'll take front end over back end. I will go with the back end. I can help Mauricio at the back end too, because I'm pretty sure the MCP will take about like an hour. Yeah. OK, Yeah. Well.
But this is the initial. Let's just say this is.
Scaffolding.
Yeah, I can never spell and so this is spring 0 basically.
In your activities, we wanna get going with all of that and I will take on the tooling as well, OK.
If there's anything that we need to do with tooling beyond just using GitHub compiler, OK.
