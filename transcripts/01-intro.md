That answers that question. Nice. Good. Yeah. It would be for us to join individually and then mute, unmute ourselves, which is not right, viable, right. Unless we were each in a phone booth all day. Yeah, exactly. Would that defeat the purpose? Yeah, yeah, it would defeat. Yeah, yes, that would suck.
Ask and and try to answer questions around, you know, the way to set up, the way to set up at scale, the way to set up with multiple people and all that kind of stuff. And I don't have all the answers, but I think we can just, you know, maybe write down the list of things that we really wanna try to get to the bottom of and and try to use the day to do that.
I would love to see at scale the use of an MCP server OK to like to layout and then process or ingest requirements. Um, like I've gone through that exercise on GitHub's skills.
Uh, deep learning thing. I don't know if you've seen that.
I should have mentioned that I so I don't have very many reps in doing these things, but I went through the GitHub training course on GitHub Copilot. Like there's eight different exercises. OK, my favorite one so far has been the like like integrate with the GitHub MCP server and like oh you're building an app that does X.
Ask GitHub for a list of repos out there that also does X and what their requirements are. Take the requirements of those applications, do a gap analysis against your own, and then create GitHub issues for each of those features you're missing, and then tell GitHub copilot to do issue one, do issue 2, and it'll add this to your base.
So it's really cool. I'm interested like it's helped me do proof of concepts by myself and I'd love to see like a team that's really kind of empowered through the life cycle that way, OK?
Uh.
So that if you can get a MCP server to look at other projects to not only look at other, well, that's that's that's that's specific example. But you're saying in general, in general, MCP server, that's a big concept. Let's make sure that we touch on it. Yep. And then.
I think the way that I summarized it is ingest requirements is also a big thing because I think I can't remember who mentioned it in that room. But I think the idea that we wanna be able to go left of where we are, we're home here in software engineering, being able to go left of it and say, OK, how do I? This is gonna be one of the big things.
When you try to apply that scale, right, is how do you take requirements and then somehow translate that into a set of task and then somehow translate that into a set of, you know, working code. Yep, yeah, OK, cool. Hey.
Yeah, we're good to know. Thanks. You're more than welcome. Can we get more fries? Can we get some waters? You can stay, though. You can stay. Anybody else? Anything?
First time I'm hearing more about the compiler tools that we have that we can have standardized across all projects. Yeah, that is something that I believe would be viable to. Yeah, get most.
Keying off that is just how can team.
Accelerate itself more than just individual development. How can a team do what to itself? Accelerate. Yeah, OK, like, OK, we will understand, like, how do I increase my velocities? You can go by all that stuff. Yeah. What does being in a team bring to the spread?
Right. So team versus individual acceleration. Yeah. Yeah. OK. And then one thing that having gone through the exercises of having no reps on this thing, there's still a concept that I don't feel like I understand that well and that's this concept of memory or different kinds of.
Yeah. So, like, and I know that's an outcome that we're all searching for, but like, I don't know what that means. Yeah. I imagine it has to do with like context versus like session memory versus like, yeah, yeah, OK.
Um.
OK, cool. One that I think I would add to my list is orchestration, which has to do a little bit with a lot of that. So if I were to create a category for MCP server, I would put that under the tools category.
OK, right. And do you want me to explain why I say that? So just basically agents, what they have the ability to do is to say, oh, what adds power to agents is to say as an agent, I have access to specialized tools.
That can allow me to do something to take a specific action, right? Yeah. So if you think about an LLM in general, it has the action that it has the ability to do is just generate text, right? But I may need some other actions. For example, I may need the action to go ingest requirements and then off of that I'm gonna go.
Generate some text. I'm gonna summarize those requirements. I'm gonna do comparison analysis and I'm gonna generate a delta of requirements, blah blah blah. But at the heart of it, I need to be able to go do something which is ingest requirements or I need to go do something which is create a PR.
Do I need to be able to go do something which is something else, right? Yeah. And so MCP servers are a way to do that. Being able to in general, the generalization of that concept is tools and being able to in whatever tool where you don't, whatever tool we're using.
Being able to define a function so you can, for example, in some of these frameworks, you can define a Python function that's going to be a tool that the LLM that you're working with can actually use to go, you know, look up the weather forecast or go, you know, into GitHub and create an issue, all that kind of stuff.
And then orchestration in general.
Orchestration in general is this ability to have a single agent use either other agents or other tools, including entity servers and go decide, first I'm gonna do this thing and then I'm going to do the second thing and then this third thing and then this fourth thing and then I'm finally gonna.
Report back to whoever called me in the 1st place. So that's orchestration. Yeah, I don't. I think that I did an exercise, but I can't even remember what the point of it was around custom agents. I know custom commands like the slash commands you can do with the thing, right? That's not agents, that's not custom.
Yeah, a custom command could be a custom agent. I think what I don't understand what that is yet or I kind of do, but I don't understand the application. Yeah, I think the so for example on the personal project of mine I wanted to have this is under clock code, right? But I only have a custom command.
That would commit my current changes to my repo. Yeah, and so I have a custom command. That custom command can start a process, but then if I give that custom command the ability to actually interact with other commands or other agents.
Then it's now becoming more of an agent, right? So the difference between command and agent, I don't think that it's super meaningful what that distinction is other than how you access them. Does that make sense? Yeah, Yeah. So under cloud code, a custom command is just a slash away and you just.
That your command and then now that command has a system prompt and it can take parameters and can just go off and do a bunch of things.
Cool, cool. You mentioned Python. Does that mean we get to use Python? I guess that's the next thing that we need. We need to. You gotta call them for a sec and then you set Python. So if you're leading the witness, I would be happy to be led that way. Yeah, I'm not gonna be super useful in terms of just pure velocity without an agent, cuz.
I don't code every day anymore, but I'm very happy to be kind of homed in Python if we want for the back end, probably not Python for the front end. It's trash. Yeah, we could, but there's a new one.
Stream lit, I think it's called it like it's basically creating a web. This is decent, but out of a out of markdown terminology and what creates the thing and it's like it's OK, OK, so we want to use Python for the back end. Yeah, what you guys want for the all good with this.
Yeah, that's fine. It will be fun. It will be fun. I'm gonna suggest probably React for the front end. That's just the yeah, yeah, yeah, yeah, the default most common thing that we probably all have to deal with. I'll see the floor on the front end. Yeah, that's fine. Are you good with that, Joe? Yeah, that's fine. OK.
Complain because everything's React. Yeah, what's that? And just complain because everything's React. Yeah, we can do something else. We can do something exotic and interesting. That's not for this kind of project. We could do asp.net web forms. And by the way, we are doing something that we should not do as software engineers is we're talking about the stack.
Talk about the what we're actually building. Yeah. Yeah. So what's probably about what we're gonna build first. Yeah. So this we'll just put a question mark next to this. Yeah, until we until we decide what we want to build. So any ideas, any things that you'd be excited about?
Building something that's gonna take at least a couple days, even if we're doing multiple things. Yeah, even if we're accelerating everything in terms of a couple of days, I think the way to think about that is something that can be iterated on. We can come up, we might be able to come up with V0 in two hours, yeah, but then we can add features.
And yeah, you can also have the like the nonfunctional requirements like I want testing. Yeah, yeah, I want good documentation. Yeah, yeah, we could establish. Yeah, these are things that are important to us no matter what our problem is. Yeah, architecture.
Yeah, not to lose sight of it.
OK, OK. Anything that we want to have, it doesn't have to be this, right? But it could be something that we want. We wish existed in the slalom ecosystem that would make our lives easier on a day-to-day basis. It could be something like that.
Or it could be something that we want to have exist out there in the world that we think would be kind of cool to have a little POC around.
Uh oh, my creativity just ran drag.
For the record, Tristan has left the room.
Don't want me bald.
What's that? The problem of confluence, right? Confluence. Yeah. What's the problem with confluence? Any sort of company confluence is automatically obsolete the second time. And it might take something right. Yeah. So if we could like use AI to like.
Manage, summarize, update.
That's more using AI rather than accelerated engineering. Yeah, but I I wonder if there's something if we can talk about that for a couple minutes. Yeah, because why? Why is something is as soon as something hits, it's documented. Basically what you're saying, it's almost out of date right away. And the reason why is because.
Basically, there is no. So there is documentation and there is source material. And I don't mean source code, I mean the thing that you're documenting. And these two things are not connected to each other, right? And that's basically why, right? You're documenting something about something else.
And then there's something else continues to have a lot of its own and it's not documented anymore. So then the question would be, could we think about things that we're documenting a lot in confluence?
And think of a way to just create this link that doesn't that currently doesn't exist and that could use Gen. AI and then we could use Gen. AI to accelerate the implementation of it as well. Yeah, so it could be it could be both ways. So let's take the base case of like how do I get on to the wireline?
How do I get home to do Wi-Fi? I think that's a great case. You do it once when you sign up for the company and then like three years later you need to tell somebody else like, oh, hey, oh, you get a new computer. Yeah, yeah, new computer. What else? It's like, yeah, OK, now you gotta go through through updated article or something.
Yeah. So let's, let's, let's. So that's that's one possibility, right. Let's keep brainstorming on other possibilities. Yeah, I think the the challenge with this one is it's, it's a hard problem. Yeah, it's complicated in ways that we can't fully control, right. It's integration with other systems.
It's, you know, creating a source master system for, you know, let's say IT onboarding instructions. It's so that's there's a lot of dependencies. Yeah, right. Yeah, right. Yeah. OK.
It's the wrong. Yeah. Trying, yeah.
Also they want us to explore kind of the day-to-day problems that we face with the clients, but that would be like.
Pretty easy to, I don't know, say just create web applications that doesn't add any value to this workshop itself. So no, but it depends on like like we we can assume that any application that we create is going to be a web application.
Right. Yeah. So I was thinking like most of the clients will have, I don't know, MongoDB management. So how do we create a content manager, a content management system? Yeah, that could be, that could be something.
Right. Yeah. We could say, hey, we're gonna create ACMS from scratch. Yeah. And you know, now the question is what are the features going to be on that CMS that are gonna make it worth creating ACMS from scratch, but.
The advantage of a CMS is that it's feature rich, right? You could start by saying hey, I just want a CMS, I can publish, you know, HTML to or use Markdown as a source, you know system and then translate that in real time to HTML using a CSS and.
And you know, publish that on the web and then you can go from there and say, oh, I want to be able to version things and I want to be able to, you know, have a have a headless mode and you know, there's all kinds of things that you can get into, so.
Yeah, that's that's a possibility.
CMS report, yeah.
3.
Or.
Um, I have a lot of ideas, but they're sort of not.
They're not fully fledged, which I think is OK. That could be part of the conversation as well, but.
So this is really out there, but maybe I'll just wait for Tristan to come back so he can hear it as well. But um, yeah, that's a little bit out there.
Gonna wait for Tristan to come back. I'm just gonna say here is.
International homes.
Tracks.
Yeah, I can. I can say more about it. Um, if we're waiting for Tristan, I'm just gonna go get some water real quick. Yep.
We'll hear it for now.
We pour some coffee. Do you want some? I'm good, thank you.
Oh.
09/13/18 What's that? Uh, that you have on the back of. Oh, it was one of the the bench or something, OK.
Where are you based? Seattle. Seattle, Yeah.
All right. Sorry. What is this? Have we said what we're doing? No, we're coming up with ideas. OK, What do we got? CMS, basically. I mean, yeah.
I feel like Ki CMS.
The other one here is like.
So was is it you saying documents are out of date as soon as they're created? Yeah, yeah, yeah, that you would put that in the CMS. So that's basically this is, yeah, OK, yeah. And then this we were waiting for you to talk about this as an idea how it's really out there, but.
That's something that's out there. It might be interesting because we don't have like, I feel like the downside of the upside of the CMS is I think there's a lot of features that we can layer on and that's, yeah, yeah, an upside. I I said downside and I was like, let me talk about the upside first.
Is that there's a lot of layers that we can kind of add on over, you know, multiple days. The downside is I think we all have a pretty good idea of what a CMS, a good CMS ought to be able to do and so like the idea generation and the discussion of the requirements.
May not be as as vivid, so it may not give us as much visibility to that process. And then to to describe the other one, I'm just gonna wait for Corey to get back.
The uh uh idea I was having uh in the bathroom was uh my project has uh like I'll just start with a a ******** story. Um.
We when I I got onto a project that was in progress and we knew that we had to create a system that allowed them to migrate a bunch of their documents for their loans into our new system.
And to be able to manage documents attached to loans in general. And so I had devised a system based on S3, just yeah, right. Like, like, OK, we're on AWS, we've got S3, we're gonna build a service, it'll take care of all the things that we need.
We'll crank up front end for uploading the documents. We'll store them all there in S3. It was gonna be simple. And then they were like, we're nervous about buying S3 when we've already bought SharePoint. Can you use SharePoint and then use SharePoint for all of the like features that it brings for managing documents so that we don't have to implement them.
Ourselves. Yeah, that makes sense. Yeah. So my architecture got shot down and that's fine. But then we just run into continual challenges with SharePoint. Our APIs don't really do the thing that you want us to do.
Oh, we don't really. Every time you tweak the metadata, it's automatically a new version of the file, even though the contents of the file itself haven't changed. I'm like, well, that that all sucks. SharePoint sucks. Oh, and also you can only have 30 terabytes of data in a single site. I mean, you've already got 50 terabytes.
So now we've got to come up with a whole mechanism for how to split that across multiple different SharePoint sites without hating ourselves. SharePoint site shortening. It's a very well known pattern. Yeah, yeah, yeah, yeah, exactly. So, so I thought what about what like like and so we spent.
The last two months building a document management system around SharePoint, which we were hoping to spend one month and that SharePoint would do most of the heavy lifting, but we're doing most of the heavy lifting to account for SharePoint's.
Um, shortcuts. Wrong tag square hole. Yeah, yeah, you're doing a lot of work for that. Yeah. So I mean, like, it makes me think we could build in three days a system around S3 and uh, React front end to drop a bunch of files, categorize them, get views on the files. Yeah, iterate it. Oh, there's a little CMS.
Specialized in document management? Yes. Yeah. As a thought, I throw it out as a thought. Yeah, backed by a selfish story because I hate my client.
And you wanna be able to go back to your client next week and see. Yeah, look, we built this in a few days. Drop the mic. By the way, if you still don't like my architecture, yeah, this for a test drive, yeah.
But I will welcome other ideas. OK, so the other idea and I'm just gonna have to spend a little time explaining it and this is just so we maybe can trigger because this is very corporate based, which is fine.
And it's a little bit.
Uh, not inside trading, but it's looking at our use cases from the inside, right? Which is also fine, so we could do that. Um, the other idea. This is an out there idea that I haven't even truly explored myself, but.
Do you all know about Pickleball? Yeah, yeah, from Seattle. Yeah, there you go. There you go. Where Pickleball was. Yeah. Main Island or something? Bainbridge Island. Bainbridge Island, yeah. It is a component of my commute to work. I cross an island. I go from the mainland. I get on an island, cross that island, get a fare.
And then that ferry brings me back to the mainland. And that's how we get to work. Sounds like a really long commute. Yeah, it is. Yeah. Same. Yeah. 10 years of that. You should stop on Bainbridge Island for a little pickleball on your way. I yeah, I have a morning workout. Yeah. But anyway, so pickleball. So tournament like management or something. No. OK. Although that's.
That could be a thing, right? No, it's a little bit meta about pickleball. We need to talk about pickleball for a minute. So pickleball is very interesting because it is the fastest growing sport in North America and North America happens to be at least the US.
Kind of leading the charge in the evolution of pickleball, OK. And a lot of other countries haven't caught up yet. And so if you were, for example, to look at some of the pickleball facilities that have come up in the US, you could say.
That there is a business model there that has been identified here, and there's a set of conditions that have led to Pickleball being able to explode here. Where else can you go in the world where that hasn't happened yet and you can be part of making it happen?
If you're trying to build a pickleball facility in Atlanta today, you're probably like five years late. Now it's just like fierce competition and there's one every like there's an indoor, there's literally an indoor facility probably every five or seven miles within a particular radius. It's just it's exploited that much, right?
So you're a little bit late, but where can you go that this trend hasn't happened yet, that you can become part of it. And so if you take that and meta from it and think about what are some of these micro, micro, macro trends that are happening within a particular Geo area.
That you can go try to apply in another Geo area. So what are the best things that North America has to learn about mobile payments from China or from Kenya? What are the best things about? And these are broad areas, but what are the best things about healthcare?
Care that Switzerland has to learn from Canada. What are the best things about public transportation that Mexico could learn from Paris? It's kind of like an opportunity hunter or something. Yeah, it's like that's why I called it international trends. It's like, how do you?
Do you look around the world? Find reputable data sources that can give you?
An insight into some trends and then see how those trends might be local to a particular area and then go validate that those trends are not happening somewhere else. And then, you know, go kind of put a recipe together of analysis. This is how it happened here.
Those were the contributing factors. You know, find out how much of these contributing factors are already here and then see if you can be the missing link there and then go do that in a bunch of different places. OK, so that's very out there.
It would all have to be manifested through an app. But yeah, you're right, there's a lot of, a lot of that work is behind the scenes. But the app part of that work is surfacing the experience, right? How do you go explore things? You have to say things that you're interested in and then the system has to take that on.
And then another part of it is it would be Gen. AI heavy on the back end to go figure out a the data sources, go parse those data sources, that software, right? Take that information, synthesize it, analyze it, make recommendations, blah blah blah. So you can imagine there could be a crawling engine.
There could be a summarization engine, a recommendation engine, and a UI that kind of, you know, puts it all together. As I say that that's a lot of work, even for the four hours of four days. Yeah, yeah, yeah, yeah.
So any other any other ideas or should we try to settle settle on a on a specific idea?
And then we can revisit our tech stack and uh, it's almost, it's almost 12. So I wonder if this is like a good time to just break, get the one. I don't know when lunch is coming or or in what form lunch is coming, but at least then we can like eat and we can haul it over in our heads rather than like.
Like the moment someone asks me to come up with an idea, that's when I can't. That's why I came up with my best work in the back. We know, because you have to go to Yeah, I know, right? And that inspiration struck, Yeah.
Uh.
So I what? Uh, do we have one lunches? I'll go ask. I I think the schedule was somewhere, somewhere in that deck. Makes sense. 12/12/30, so.
1230 Tristan Yeah.
All right. So maybe let's come up with an idea right now. Well, let's see just to kind of try to get the juices flowing. So pros and cons of some of the things that we've talked about. So, so you said this is basically.
Uh.
A subset of this, yeah. So we basically have two things, something that a, you know, super out there. We basically have nothing in here.
To start from other than a very vague idea of something, right? Yeah. So I think the pros of that are we probably can spend 2 hours this afternoon talking about, OK, what are some of the components? What are some of the features? Is it doable? Blah blah blah.
Realistically is a little bit earlier than most of us coming to engagements when we do build engagements. Yeah, because usually those things have been worked out already if the requirements don't exist. So I think of that as a con.
Of that as a con. And I think of the of the pro as it's not something that anybody else is gonna come up with. So it's true. It's fairly, fairly original in that sense. Yep. How about CMS or CMS slash document management or CMS specialized in?
Document management, Yeah, the pros are OK. So the pros are that the outcomes are relatively deterministic, like it's a site that can manage a bunch of documents and get a cool view of the thing with non deterministic practices as opposed to international trends.
Which is like essentially using accelerated engineering to build an accelerated engineering app. And I'm worried that that's too much nondeterminism for like 3 days of work, but it might be fun. So at least like, yeah, I don't know, that's I like. I think it's easier to gather requirements around a thing that is like.
Clearly about managing files and representing them in a nice way. Yeah, so I could be wrong. Yeah, but you're right, Khan is. It's dreadfully simple, predictable, and it's probably what everyone else is already doing.
I like the the um the the approach that we took with our front end was uh I don't know if you've ever uh I I'm not a modern web guy but this thing called like index DB anyone yeah smiles OK like it was a cool way to like have.
Like to apply accelerated engineering to crank out a bunch of code about a front end that was completely unfamiliar to me. So that would just be on the project. That part would be cool to to do the file upload part like like like drop 100 files onto the browser.
And watches the the browser has code like kind of in the middleware that manages the upload for you. Oh, I see. Yeah. OK, OK, yeah, that seems like. So it it it's a good opportunity to layout some some additional behaviors to use Landon's terminology about how we would approach building the application before we build it, yeah.
Right. Yeah. I like that. Yeah. Um, then what did you call it? Index. Uh, Index DB? Yeah. Yeah.
For the UI, yeah, not just a three tier application, but like kind of like a like the four tier with the sync engine. Yeah, yeah, yeah, he understands. I don't. So.
You might want to do, but they they would not hear CMS or.
Something else and it's doing it in a way that's consumable by. So like a CMS that's built off of maybe uses a get repo and marked down as its back end instead. We usually build database right? Mm-hmm. You can't really.
Query a database with uh, Jenna. I really like late, so what's important? Does that make sense? Yeah, yeah, yeah, I think that's something that's more. So there's an interesting concept of.
Can't remember what the name of it is, but you know SEO, right? Yeah, Yeah. So the new thing of SEO is how do you do optimization of your content, but for AIS exactly. So I think it's.
AIO or something like AI, you know, but but it's the same concept. So if you think about most systems right today, it's here's a system, here's a data store behind that system.
So this is just a bunch of components here. This is a data store or you know multiple data stores and then I have some type of a UI here to go to have users on this end.
So the users use the UI, the UI uses the services, the services get access to the back end systems, right? What some people are starting to think about now is that the users are here, they access an LLM.
And then the LLM accesses either a set of services or maybe this is the set of MCP's and then the set of MCP's has access to the source data. So now you're optimizing your content.
And your services not so that they can be surfaced with an AI UI, so that a user can use the UI. You're optimizing them so that they can be surfaced to an agent and then the user is using the agent.
And so where that's relevant in what you were talking about is, oh, can we build ACMS that is basically AI native?
And has MCP interfaces for agents. Well, so OK, the thing to think about is.
Think about indexing a database, right? We don't index a database because we can't query it without indexing it, right? We index it because querying it without indexing it is extremely inefficient.
You can't create. Does that make sense? Yeah. So it's it's it's almost saying, yeah, if you if you had a bunch of markdown files and you had.
A million markdown files, then yeah, you could ingest them all, but then you couldn't really efficiently go after the content that's in it. So to go efficiently after the content that's in it, you you define some kind of interface that gives you access to it.
It's a deep, it's a deeper conversation, but yeah, no, that's a like it makes him relevant in the context of.
That's a whole. So Tom, are you suggesting part of the CMS doc management? If we were to go that route, would also come with an MCP server that we could build an agent around? I'm saying when Joe said what he said, that's what came to my mind. That sounds cool. It is.
I not only do I have a document management system, but also built into that management system, I have a way to interact with it that doesn't require me to use a search box. Yeah, right. Yeah. So it's like it could be, it could be, for example, right? It could be summarize.
All the engagements we've had that have included Salesforce, right? You can't do that searching through SharePoint because that's going through SharePoint. You would have to go find all the engagements that have involved the Salesforce implementation. Yeah, then find all the documents that have to do with those.
Engagements then bring all of those documents together, probably in some temporary, you know, storage space, then ingest those documents into an LLM and then ask the LLM to summarize it versus using our new Fangle CMS DMS.
You can just say summarize all of those and we just yeah, take that and basically do all of these actions. So oh, that's a nice room. Yeah, jeez. Corner office, only the best. I chose it by its name, but I really nice place.
They have Windows. Does that? Does that make sense? Yeah, yeah, I think so. It's just kinda like quantum leap in a way, but like on a grander scale, like like you can upload. Quantum leap was a different idea, but it was. I thought it was like you could upload project artifacts and like have it summarize those and then write queries against them.
Yeah. Cloud weight was like, yeah.
And starter. It's just like the framework for pen. It's like you dump your stuff in and it's like, here's your epics, right? This is more.
Generic. Yeah, generic. Abstract. Yeah, you might be able to get to build product requirements. I don't want it to build new products. I want. I want to dump a bunch of files and then ask it a bunch of questions about my files. Yeah.
Whether they're pictures or PDFs or spreadsheets, is that like enterprise knowledge management? Yeah, yeah.
Yeah.
With a cool visual and an MTP server.
Four days, three and a half.
So whatever, any other ideas that come to mind based on the things that we've talked about so far to do app, but to do app that reads your mind. Yeah, so one of the teams I'm gonna build like.
Um, basically like a financial app to track accounts. They're gonna make it multi tenant.
Have some kind of like shared ledgering system with individual user accounts. OK, another team said they were going to build like a project tracking system or something like that.
We have to do that. That was my next suggestion. Some sort of so we don't have to use that anymore. Steal client idea. Yeah, yeah, steal an idea of, you know, something you've worked on for a client now. I kind of did that with our document management idea.
Sick my client's ****. Yeah, we have an out there idea and we have a more slalom grounded idea is what we have so far. Well, we're we're we're making inroads on taking that slalom grounded idea and adding a bunch of crazy **** to it. Yeah, which I like. Yeah, yeah, yeah. That's how how we I like that.
Yeah.
Anything else that comes to mind?
OK.
That looks like a vulture.
I don't like it when vultures are circling around. Yeah, a game in Unity or something. We could, I don't know, we could a Jackbox. Yeah, that's actually something I've wanted for like a software or like a connect or something.
Something to like do live polling, like scan a QR code, like like do your votes or whatever and then like watch the the projection rerender itself live as people start putting in their answers. Mm-hmm. So like kind of like Jackbox, but for just.
Let's type up. I don't know which. Well, that's sort of a trivia game, but the cool thing part about it is like everyone can like log into the website on the phone. Super easy. And then you play like scan like somebody. The interface on your phone renders like a room. A room is created for the game.
And as the game does itself, it kind of like Ajaxifies pushes like what your phone should be showing to you. It like lets people respond to questions with bugs, but it also lets you draw pictures on your phone and submit them. And then you can compare them with like Pictionary Family Feud.
Yeah, yeah. OK, so cool. I like that idea the most, actually. Yeah, especially what do you call it? Jack box. Well, conflict box. Yeah, Jack box. I'm even better at conflict box. Jack box variant. Yeah, yeah.
Uh, and then it's a. Is there a chat box with variants that could be?
Useful for slot of work. Yeah, yeah, Slack channel. Pointing poker. Yeah, you log into a room. That room was set up more like a pointing poker room, right? Yeah. So you just enter a room code and then suddenly whoever is running the thing can just be like, this is the story we're doing.
And then it shows up on everyone's phone. No accounts needed or anything. It's like ****. And then it's like, oh, 15 people said it was a three and one guy said it was a 17. I'm sorry. This is a good idea. Yep, Yep, Yep. And then or change it. And then like, we've got a polling. Yeah, yeah, this is it. This is it.
This is it. This is it. It involves back end. It involves dynamic front end, maybe webhooks or something. Slack integration. Yeah, sure. Why not? What's the slack QR code scanning?
Have the display. You already have. Oh yeah, do it remote that like you. Everybody doesn't even have to be in the same room. You just like have like a pull or something. It has a QR code. You can put it with your phone. Yeah, like this is the way.
OK, all right. See, you're already coming up with more ideas. We have 20 minutes. Now what do we do? Now more ideas. OK.
No, I wanted to just kind of leave that there for context, but OK, I can scrunch it. Do you want you want more? No, it's just gonna start questioning out this idea. Yeah, yeah.
I would like a different.
This is a microservice for each each kind of app that we have. No, no. OK, too crazy. That's a good idea. Don't worry man, Jenny and I is gonna crank all the things out.
It's horrible. It's like, oh, you just spin up new microservices, yeah.
Uh, have a concept of like rooms and uh like users within those rooms somehow getting back into your session. So what's the not not to be too?
Grounded because I don't think we have to be grounded, but I'll just ask the.
Um.
Good question.
What is the problem we're solving with that?
What's so hard about pointing stories with cards or?
Digits and this so that it's not a pointing poker application. That is just a a use case. It is an actual application of it, right? The point of Jackbox is not that it is a is that it's a game. It is a foundation for building an extensible like.
Like they they've been doing Jackbox for like 12 years. Every single player goes to jackbox.tv on their phone to start. They enter a room code and then like that room was created around this game. Each each pack is like 6 different games.
And there have been like 12 of these packs, right? Like, so this this site is capable of just like and Jackbox is like a board game you'd buy at Target. No, no, no. It's like a a game you run on Steam. Like someone runs the game on their laptop. OK, so I'm gonna launch Jackbox Party Pack 2.
And within that I'm gonna run the trivia murder mystery game, OK? And then then that creates a room code that is like ABC5, right? And then someone on their phone goes to jackbox.tv enters ABC5. Yeah, the site.
On the phone now re renders around this concept that we are playing Murder Mystery 1 on Jackbox Party Pack 2 specific to this session of people. Yeah, and then it like renders a murder mystery trivia game. But Jackbox is specifically that platform is for gaming, right? It's so.
Could you? And this is, I'm just educating myself here by having you educate me. So Jackbox, what if I said crazy idea? Hey, why don't we use Jackbox for Storypoint? Yes. Could I do that? Yes. I mean, no, not today. Not today. Not today. Because Jackbox.
Jackbox.com or whatever controls ******** games. What the use cases are. Yes, yeah, exactly right. So it builds a platform where someone runs the application on their machine and then everyone is like Mauricio could work on the pointing poker.
In the game, yeah, while you're working on the like, is a hot dog a sandwich game while Joe, you know, like he builds us a platform where we could all go in different directions. But then like, all right, cool, now we're using version one of this thing. We've got four different games to play here, so I'm gonna hit start on the second one, right? Scan the QR code and then everyone's phone gets into.
OK, OK, cool. You have more space on the on the so. So do we want to brainstorm on more ideas or are you ready to into chat box Mauricio, you can be quiet. That's your that's your perspective. I mean I I'm.
I'm really trying to figure out how that box is going to make us use as much resources as we are intending to learn here. So yeah, I'm I'm just listening to your ideas. I mean, there is, there is, yeah.
There's clearly a back end. Yeah, there is some complicated communication between the front end and the back end. Definitely. There is potentially A dynamic aspect to the front end. Yeah, that can be built off of your use cases or your use case category. There is customization.
Opportunities. There's a lot of discussions to be had on how do we come up with the first few use cases? Is it hard coded? Is it pointing is one thing or is it does that thing belong in the category and we're actually creating a category and letting people reuse that category for different things. So I think there's a lot.
To mind there. And then there's obviously we can build as much complexity as we want on the back end in terms of microservices and you know, different data stores and all kinds of stuff. There's at least two front ends. There's the user interface front end and then the display front end. Yeah, the admin front end, right. Yeah, the display.
The admin is the one that starts the game and then shows the game. Everyone like sees it. If it were projected on a giant screen, right? Like yeah, then I I I guess I envision it that it it shows the game as as having conceived by the admin it started.
And then like while it's showing it, it like like let's say it's a live polling version or pointing poker. I guess it's the same thing, right? But like like then there's a QR code so that people can scan it on their phone and join and it just shows like, all right, we're either pointing the story or answering this trivia question.
And like the and pushes what we're looking at to the phone so that they see like they don't have to look at the screen, they can see everything about it on their phone as well. And then they see an individual version of what's on the screen on their phone and then if they want to see the common version.
Like a tally of the score or a tally of story points. Yeah. Then they look at the screen, correct. On the on the phone, they see their own. Yeah, yeah, yeah. And then that you does that. Does that? Yeah, I'll clarify some little things. Yeah. Yeah, yeah. And there's still be communication, multiple front ends, a back end that's capable of dealing with.
Not just like a game, but like the foundation for all of us to go do our own. Yeah. And what's really interesting to me would be how do we think about what these use cases are and how do we abstract them? Yeah, like how do we come up with an engine that can deal with a story pointing session?
In the same way as it can deal with a trivia. Yeah, or trivia or in the context of work. Let's just say for example a training session where you wanna have a a quiz at the end of each section that you go through. Mm-hmm. Right. Mm-hmm.
Right. What's the abstraction that we come up with to that is, hey, I have a set of questions, I have different answers, then I need to be able to vote on those answers and then I need to come up with a single answer to that question. That's a consensus across all of the, for example, right, across all of the answers.
Probably having versioning of the same trivia as well. I mean because taking into an example what Dom was saying about the training session, we're going to have this training in different regions, right? So probably we will need to have like different versions of the same content that we can display.
Right. Cool. Yeah. I'm hearing a lot of consensus on Jackpot's idea. Yeah, I don't know if we can call it Jackpot. Can't call it Jackpot. Wait, wait, wait. We could call it como de Dise Jack.
I have to write it down before I can announce it, but I might have a chance. I'm going conflict box. Conflict box. Conflict box. Like Gaja is J, right? Yeah, yeah, Gaja. They conflict them.
OK. I mean, I think that's a pretty good brainstorming exercise. Yeah. Yep, we got there. Yeah. OK. We can come up with screens that storyboard our way into this thing. And it's like, yeah, so, Joey, you're good with this idea. Oh, yeah, Mauricio.
All right, let's go. OK, so we're going to revisit this in a second, but here this. So I would like to, I would like go last step for this, say what is the problem that we're solving?
Let's just sit on that for a second, OK, 'cause I think it it is something that a lot of times we have to talk to our clients.
And a lot of times, I think, especially as technologists that come into the conversation, we come into the conversation and we're expected to be the technical people that are going to work on the solution. And sometimes our clients want to be prescriptive about what the solution is.
And not spend enough time talking about what's the actual problem you're trying to solve. Because you may be over here trying to come up with this, but really, if you knew that these things were available and could actually solve your root problem, you could be over here and not not over there, right?
Yeah, Mike. So I both of my the ideas that I was really excited about were focused around selfish goals like as a but the document one as it was as an architect on this project where the client chose something against my architecture and watches it sucked like I wanted to show that we could.
Could have done something cool, but this one I like better from a social perspective like a like slalom build we have, we have tech talks, we have connects, we have, we have various things in which we have a projector and we want to raise like.
Engagement with the audience, with things that are about what we do, or like a platform where we can establish new logics. So I like that it's it's raise.
Engagement.
In.
Work functions, training functions. Uh in what in in basically?
And yeah, raise audience engagement. It's all events. It's all events, yeah.
I was thinking we have something projected in the gorge, projected in the gorge or shared from your screen on the software engineering connection you did. You know what I really like about this potentially is if we come up with something cool, it could be something that's reused at the next town hall or whatever on a pretty good scale. Yeah, we have sometimes.
Thousands of people are out of town halls. So yeah, and there's like, like we got like Spark think for doing surveys. Like we have some tools that are out there, but like, they're not for this. Yeah, like, yeah, yeah, they're not for, they're for e-mail. Spark think.
For live events, for live events, there you go for live events.
Today.
And with the goal for it being extensible by software engineering leaders all over the place. Like if I wanted to come hop into the repo and build a new kind of game into the repo, like that's not a that's not impossible. Oh, OK, I can add to my.
Yeah, sure. Base platform, you know, profit microservice, but that's the idea, yeah.
For extension, like we'll know it's a success when we show it to this group and then like, I don't know, Ryan Anderson's like, oh man, I would love to have this kind of game. How hard would that be? And it's like, oh, but you're just a prompt away.
OK, I like it. Built in prompting resources for how the repo works. Yeah, so they can just, yeah, like, hey, I want poker. I want, yes, I want pointing poker and I want actual, oh, actual poker.
Blackjack itself. All right, well.
OK, it's a good starting point. It's almost lunch. I think we stretch now. Now we stretch. It's so freaking flat. Whoa, what's over there? Houston. Oh, where are we? Also Houston. We're in an area of Houston called City Center, which naturally is not.
There, which is city center. It is not at least two city centers, yeah.
So, or is that whole thing? Oh, OK. And where are we? Oh, we're here. Oh, we are about sitting center. Yeah, that's really bad name. Yeah. It's like I used to be a member at a club called Midtown Athletic Club, which was nowhere near Midtown in Atlanta.
But it's apparently near Midtown in Chicago, which is where it started. I was in Atlanta for the for our Game Jam hackathon. Yeah, like, yeah, I saw you there. Yeah, a couple years ago. And like, I can't. Was there a recent transition to a new office or was there about to be?
I think this was this pre COVID we were in bucket.
And that might have been where you were. And we were in that. We were at a place for the event. Yeah. So we weren't even in our office anyway, 'cause I remember that event. We had to go somewhere else. Yeah, yeah, OK. But pre COVID, we were in in Buckhead and then we were planning the transition.
To our office where we are now, which is downtown and COVID happened. And I think that summer we moved into the new office and then nobody got to see it until that's right. So I didn't see the new office because the game jam was post happened.
But I don't. If it's the event that I I'm thinking about, I don't think it was held in our office. Definitely. I saw someone scooting around the office. Oh, yeah, yeah. Nice like new kitchen area on the corner. Yeah. Yeah. Yeah. OK. With a view of the the of the scooting thing. Yeah. Yeah. Yeah. Yeah. Yeah. OK. OK. So you saw it.
OK, cool. Cool. Can we, since we have a couple minutes, can we try codecs on all of our? Yeah, so go to your command line.
You probably don't have it, but oh yeah, go to your.
So I would say probably the best thing to do would be go to ChatGPT first and see if within when you go to ChatGPT and you go to the side menu. Do you have codecs as an option there? Oh yeah, I do. OK, when you might go to ChatGPT, go to chatgpt.com and sign in.
With your asylum credentials.
Yeah, Microsoft. Yeah, we're no, no, no, not Microsoft account. Go back. OK, Put your slot on e-mail. OK. Or yes, like Jack, just put your slot on emails for things like pointing poker or live polls or something that we can show on a projector.
In the gorge or during a software engineering connect to raise engagement from the audience in slalom. Hell yeah, we got this. They send you a quick. That's what I was telling you. I was like, think of something that can impact slalom. I thought it was saying something else. Can you go back to it, Tracy? I have it. I was talking about. Get a quick to sign in.
We'll send you a code, so just you have to say something, yeah.
Y'all feel like you're you're on the way now. Yeah, we're exploring whether we have codecs, whatever that is.
So is Codex the one that's the CLI tool from Open AI or what? Yeah, OK, so only you probably have it and I probably you you might too. I have it within. You have to install it now in your command line. Oh OK, so what do we do do an NPM install NPM install Codex.
Oh, OK. The other thing you can do if y'all are interested in trying other tools, then a dash G or something. You can point like open code or client to like our Bedrock instances or use your GitHub. Just know that I actually say that again.
Open code or plan tour bedrock. Yeah and and open code. Like honestly, if I wasn't, if I didn't have the intention of teaching everybody stuff and I'm using like just plot code and like cursor and Copilot to teach people the basics, open code would be my favorite. Like I actually really like open code is like a CLI, a CLI interface that can.
API into any of the other ones. Yeah, and it basically says like it can sit right on top of pod code. For example, it adds another agent in front of it, but it it does some more standard stuff that I OK, can you um can you send the info for the bedrock instance that we can point to?
Yeah, you basically just go to innovation labs and there's a model there that you can consume. So any innovation lab that you have, you go and then select the bedrock model and you get the key through it and you can use that to access. OK, so you can like your outline. OK, should we get access to?
Um, I'm just a little.
Yeah. So you you don't have access to it. No, 'cause you don't have Ted TPK Enterprise. So I think that's the. I think it's only you and maybe Tristan said that I have. Did you? Oh, I also, I have the free plan for complete. Yeah, yeah, yeah. OK, OK. So you want we only have a few of those licenses, Andy. OK.
Um, so open code does what then? Does uh open code? It's basically works exactly like cloud code. It's an agent in front of like an LLM. So you can point it to another service like Copilot or cloud code as to what backs it.
Or you can point it directly to an LLM model like through Bedrock or through Azure. So and through Bedrock we can get access to cloud, but we can get access to. Do they have open AI models yet? Yeah, they should. Through Bedrock you can probably get the GPT models inside as well.
I'm not sure one of those was missing last time I last time I checked. I can probably exit. Well, you're going to add that on that. I'm checking.
Um, but you also could go to the Azure. Uh.
The Azure, yeah, but we wouldn't get anthropic through that, right? Yep, through Azure. Yep, you go to Azure and you go to the Open AI models and choose models. Let me that might be. I think that's the one that I accessed most recently. So let me just see.
You just got to choose that model and activate it.
Yeah, he did it for that workshop, the the boot camps. Same thing, same process. What are we talking about? Go into Azure and activating a model through. Oh yeah, actually Michael J helped me set that up. It was like an 18 step process. I probably remember like the first five of them.
Right now, if you wanna do that, you don't have to do that, but I think that's a good way. That's a good way to do it, so.
So I think I have a resource here for the boot camp. Yeah, so basically when I go to open AI, like I think it's called open AI if I'm not mistaken. So AI marketplace, I type it up and search again.
Here at the top here. But like, yeah, opening it. Yeah. And from here you can create like a new, like a create thing on the top. Yeah, but I think we had one already. But you want to create one for this. Well, you can. I mean, it's OK to make use cases, but you can make it.
So you can make one right now for the immersion thing and you can yeah, the keys to everybody here if you want. Yeah, yeah, so, so.
So create one.
Dropped in the eye.
So I think it'd take the first year to have a resource group and yeah, So what resource group do I want to use?
Hey, OK.
I think we should just call it Caja. Caja. Yeah, it's gotta be something small. Oh, Caja. OK, OK, Caja. It's just it's just a box, though. It's right, exactly. But in Spanish.
See, I mean, like, I think I think that's because two things, two things. One is box, which is a callback to a throwback to Jackbox, but it's it's distinct from that completely. It's Spanish, which is welcoming. And three, it's like, Kha.
You know, which is the platform where you know, like the how would you say, how would you say in Spanish thinking outside the box.
I mean, but is there like you understand what thinking outside the box means in English without translating word by word? How would you say that in Spanish?
Is there a is there a a a shorter way? I'm on board if you call one of the games. It will be like regionalism.
But uh, for example in my city we can use uh.
Only saying like thinking outside itself without box. OK, OK, this is what you're talking about. I'm working with sorry to distract you. I'm working with Microsoft Games Division and they wanna use generative AI for localization. But part of the localization is what you just said. It's like we say like what's up dog.
America. But what's up Dog? Translated to another language doesn't make any sense 'cause they don't contextually say something, right? Exactly. It's it's actually like a really neat problem. Yeah, it's been kind of fun.
But Jen AI, like the models themselves are pretty good about that. Yeah, exactly. Yeah. Am I gonna run into, are we gonna run into rate limits on here or you think if we access the API directly, just hit it and if you hit it, then don't. I don't think.
You should, but you might. OK, so uh, January immersion pilot creating. If you hit the limits, then try one of the other options.
Or or go beg MJ to reduce some throttling mechanism he has control over. Well, if he has control over it, then it should be good. Tristan can phone an old friend, yeah.
K.
Oh.
Alright, so now that I have it, uh.
So here, can you give me a hand here? Yeah, so now you should be able to create like a model underneath it or something like that.
So yeah, there goes.
I don't remember all the terminology, but you can basically create like a little. I think, um, I have to go to this portal. No, the foundry portal. Oh no. Yeah, maybe. Maybe they can just up there. The AI foundry portal. Yeah, that's where you go. OK, I thought it was like just for data pipeline ****. No, I think that's where you go, 'cause then.
Go here and then go into deployments. That's what you want. And then I want to deploy a base model. Yep, that's it. And now you type in like, well, so let me see if I have access to. There's Codex, by the way, you're talking about.
See, there's no, there's no clod, not type sign.
Seriously. Yeah, through and like, there's no way I could have sworn you sounded on here. So that's for sure. Codex, Mini, Sora. See, those are all open AI models. I guess you could.
And if you want Sonic, use your Copilot license. Again, like you can use Copilot as the back to something like open code and still access the Sonic model through it without API access to Copilot. Yeah 'cause it basically what it does is open code, for example, will just implement the agent of Copilot and it'll say like hey.
Sopilot use this model, right? OK, so let's do that after lunch. Just kind of settle in on our tooling and then we can come up with the way that we want to set up rules and things like that and the way that we I think before we have.
Have an in-depth discussion around our requirements. Let's talk about how we want to capture them and convert them into. Let's talk about what we might want our pipeline to be from requirements to user stories to acceptance criteria to tasks to actual working code.
