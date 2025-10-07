All right.
So now with our newfangled.
Um.
Plan for the AI docs I have the chance to modify.
Like there was a story that we had to find for.
What was it? The make file? We're doing a make file so that we can orchestrate both the front end and the back end as we go.
Mauricio did a make file for the back end, which I had to move to the front end. So we like got a partially partially implemented make file that only focuses on back end stuff. So issue 26 is to expand that make file.
But when issue 26 was created, there was no make file. So the plan that is created is to create one and I'm like getting the a chance as a user to modify the plan to expand the file.
Start back in, start front end, start all, stop all, restart all status.
Test back end, test run in, test file, test watch, test coverage.
Some of these commands.
Foul.
So I'm going to modify this to say we need the things that do these commands, but evaluate strongly the commands that we have for overlap.
Make them match the below and there are deviations.
I'll just catch you up. I am since the we I created the issue 26 to create the make file before you would create the make file. So now that there we're in a situation where I wanna now we have a front end and a back end and I want to do issue 26 to make the final version of.
Orchestrates both things cool, but I am using my newfound superpower landed enhanced process to modify the implementation plan before it begins.
Process management system create dev processes directory management.
Wow.
So with implementation plans, generate one. Do we then just edit that directly? Yeah, yeah, it gives you. So as you can see in the lower right here, it says type proceed to continue with implementation or abort to stop. Mm-hmm. So I get to all the chance to make tweaks to this thing.
Get ignore updates, add depth processes, unit testing for make file targets. Cool integration testing. Sure, why not?
Python 3 plus with poetry installed node JS.
What is the?
What's the version of node that you're using?
The record state we are changing node to 23 plus.
I have no idea what a modern version of the new make is.
Pipeline Committee.
No, it's working.
Hello.
Oh, I like that it's given us an estimated effort. Make file core implementation 4 to 6 hours. Testing and validation to three. Interesting. I should probably get rid of those estimates.
Why? Well, because they're they're irrelevant. Four to six hours, we'll be done with this whole thing.
So you just refined. Yeah. What is the actual estimation of work that we're completing?
Uh, OK, I'm gonna say keep all those and I'm gonna say proceed.
So at the end we can come up and say, hey Landon, we created an application that is, I don't know, 1000 hours of work effort in three days, right?
So I still have a bunch of Infer stuff to do, yeah.
What is the?
Status of the Do you have a command now to create an issue or Oh no, we said that I was gonna create that. Yes, that's right. Yeah. OK, I was. I'm just stuck in. Also, I don't know if you like you can you can choose to spend your time on it, but like we can also just say create an issue that.
Yeah, like in in the prompt and it will it will go do that. Um, like I would say a simple sentence or two is enough to create the foundation of an issue and it'll create the template. It'll create against the template, but.
Did you have? You didn't have to specify the template for it to create the cancel template, no.
Although like if you wanted to, that's probably where you could enforce some certain rules like like tag the issues and tie them back to our original features. Yeah, because that's the thing that it won't naturally do without a lot of guidance and that would be a good value add.
E.
Mauricio, what's the next back end issue that you're going to take on?
Was about to take a look into that. I'm not pretty sure.
I wonder.
There must be some kind of data foundation for our activities. Like our activities have to be able to capture a whole bunch of user input and make decisions about how to render that right? Like starting with something simple, it's like.
Pointing poker like the admin is going to define first ask question one and give them these options and then the users are going to say I said this, I said this, I said this and that activity is going to receive data that makes sense to that activity, but it's going to be delivered.
A back end that's kind of activity agnostic. Yeah, that's exactly what I was thinking is that there is a foundational data structure that's basically activity. So a session is a grouping of activities.
An activity is a grouping of questions, basically, and a question is something that has a statement, which is a question and a set of possible answers in the case of a, you know, multiple choice question. Yeah, or.
A question that has a, you know, free field answer that people can just type in whatever answer they want, right? You know, like for the word cloud example for example. So we should so we need a data model and.
We need something that's gonna implement that data model and deploy it out to Postgres. Yeah, um, and uh, yeah, we need a service that's gonna take.
Information that can take the generic data model and say this shall now be a planning poker session or planning poker activity right which can then be in a session and so for planning poker activity.
The questions are maybe there's only one question and the possible answers are 12357, you know, 5813, whatever that sequence is, right? Right. So.
I'll say a thing, I'm not sure if it makes sense, but like I that Postgres data model has got to be so general purpose like and I think it I think Jason or I think Postgres has got like a a Jason data type.
We're like some blogs, right? So yes, because but like, so I think what is the what is the view layer, the thing that like shows, oh look, this is the question that we're showing and here are the votes that they're coming in. Yeah, um, like it's gonna need to be able to say.
Every two seconds pay back and tell me all of the user inputs for this activity and this like or yeah, just this activity within this section. Yep, and it's going to be like, OK, here you go, the activity specific.
Participant layer defined the data structure and the and the. I think the data structure stays the same. I hope not because every activity is gonna have a different set of requirements, but they're all going together for example. So the pointing poker is gonna be like.
This is the activity. This is the question. I said five points right? So like so so so that for that example it's label of the activity, yes.
Verbiage of the question, verbiage of the answer. Take another activity example and see if it's different. OK, let's do the the live polling. Yeah, OK, so live polling is the activity type live polling.
I'm Joe and Uh and I think that uh, Dom is back, thumbs down, right?
That's it. Like that. That's the one response. Yeah. So again, label of the activity polling. Yeah. Question. What do you think of Tom? Right. Potential options. Good, bad, outstanding, the best ever. Yeah, right.
Yeah, so if it's the same structure, it is the same structure, but I feel like like like this is the user inputs table that when on a live activity.
Regardless, I've got a new layer and I'm going to execute the following query every two seconds. We'll say select star from user inputs where session ID equals my session, where activity ID equals my activity.
And then you're going to give me like 5/10/50 JSON objects. The structure of the JSON object is established by the view layer and the participant layer, right? Like it's one repo, it's one repo that or not one folder 1.
One service sub micro service micro front within this thing right? Like we have an activity folder so like the like the front end gets to define the the the structure of the user input for itself.
So you know what I'm saying? Like it's just a JSON object. It could be anything. It could be anything.
Maybe, but I'm just wondering if that's more complexity that we need. Can I can I draw something out for you? Yeah, yeah. So let me get session ID, activity ID and.
User response.
And the user response is what is.
Open-ended, right? That's what I'm saying. I don't think it needs to be. I think it has to be. Yeah. So, OK, you might be right. We might be able to put some guard in the way that I'm thinking about it is session. Yeah.
Session has.
Activity has questions, question has, might have questions, answers, might have answers.
That's all depend on the activity. You mean an example of an activity that doesn't have a question with the list we have? Yeah, go back to the list.
Uh.
The word cloud generator activity could not have a question and just yeah, people and their inability to free form. What do you think? What do you?
Of slalom.
Or cloud, the answer for that so has potential answers. One type of answer could be free text, another type could be multiple choice, right? But there's going to be so many activities that don't have multiple choice. There are going to be so many activities that don't have free text. There are going to be activities that have both.
None that matters, OK. None of this matters.
From the API, so some activity.
That's already Chinese store.
USA.
Excuse me?
We can have.
Yeah, yeah, that's the answer. The answer is nothing. That's that's what I'm thinking. So yeah, the the reason why I'm going through this is to say, you know, maybe question is not the right term, but it's almost like this is the statement. Maybe it's the question, maybe it's not, but it's the statement that we want the end users to react to.
Right. That's because this is ultimately this engagement, right? A logical data model, OK. And what I'm saying is on the UI for the participant view, right?
The thing that's gonna show up here is shall we call it a question just for the for the sake of the discussion or call it a statement? Let's call it a statement, right? Not a question. So.
Here at the top I have a statement, right? And here on the participant UI I have.
Option one OPT one the the live responses OPT two what's that the live responses that be it won't be necessary options. So for the participant it would be you know what we're asking the participant is provide us your answer. So this is participant.
Right. And then this is, what do we call it, a viewer?
Right, so on the viewer the viewer you have. Of course this is simplified, right? But statement here. And then on the viewer you have you know option 1-2, option 2-3 people chose that, option 311 people chose that.
Right. And that's the thing that gets updated in real time. Yeah. But the reason why I'm interested in this as the logical model is to say agree with you the statement, the type of statement might be different. So there's a statement like this and there is another statement where this is just a field and you can type whatever you want. So this is what I object to.
OK, the activity may not have a statement. Maybe there's like we don't want to pigeon hole them into a specific data model at the activity level. This and this is 1 application that follows this paradigm, but it's like.
We leave it. We leave the responsibility of what they expect from a user up to itself. The activity gets to define what the user says, and the activity gets to define how it is stored on a user by user basis. But like the system stores, the system makes it easier for the viewer to simply say.
I am a viewer representing session one activity two. Give me all the user responses and it's like oh T Rex gave this blog. Use the blog that you gave me front end and I'm giving it back to you for your viewer front end. But you get this up so.
T Rex. And then where are we doing dinosaurs now? It's not T Rex. When I when I sign up the jackbox party pack, it's my usual. OK, alright, alright, so and then other person and then other person and then other person and then.
What is it to the user codes? Nope. It's the user response. It's just a JSON. Oh, user response the structure which is defined by the front end that both allowed the user to give it and will display the. So it's not unanimous to say by the activity, yeah.
Yeah, I'm not opposed to this. I'm just gonna say for the record, we chose to and we don't. Doesn't mean that we can't go back on this, but we chose to have a relational database. Yes, being able to do this on the viewer with the relation database is super easy.
Being able to do this when all of the responses are tallied up in a JSON BLOB inside of your relational database, it won't be as easy. We're not talking 10,000 response. We're not talking million response.
We're talking, yeah, within an activity 100, yeah. And also the ability for that activity to evolve over time, like those user responses. That's true. That's true. We don't want. OK, I'm OK with it. Either way, I it feels a little bit like a premature optimization to me.
Like the all the activities that we're thinking about right now I think are statement type activities. Or are we thinking about something that's not a statement type? I would argue it's trying to establish a hard guardrail structure for that data model is the premature optimization. Like this is the premature simplicity.
Like we are just allowing the we are we are giving the guidance that the activities themselves get to define how they expect the users to respond to respond and that we have like we as the application have no no stake in this data. We don't care what they store. We don't care that they store anything. We do care because we want to be able to report on it.
That's what the viewer wants to report on it. Yeah, the viewer is the one that's establishing the structure anyway. I think it's the one application. Yeah. So as the viewer now I'm gonna have to go into my relational database, retrieve all of my Jason blobs exactly, and then manually tally up across my Jason blobs. Correct. So OK, that's yes, exactly over the.
No, but easily like like like.
We don't know what kind of activity we're going to come up with next month. We don't know that it's going to have statements. We don't know that it's like all we know is that you see how that's the premature aspect of it. It's like you're trying to do something today for something that you don't know whether you're going to have to do or not.
Tomorrow, like that you'll see the naturalized, right? See what you're saying? But this is the foundation of architecture. This is like.
While we set up our modules and modularity, OK, yeah, let's proceed.
I do. I do see that that interpretation is accurate, but what the the the point of bringing a structure like an enforced structure to this thing implies like a system responsibility that I don't want.
Yeah, that's that's that. That's why I'm saying this. It's like I have no, I don't care **** about that. I care about, I care about that we can gather user inputs. I gather that I I want to gather that we have sessions. I want to gather that these sessions time out. I want to delete this data in two days. You know, like like I don't like none of that data is relevant.
Report long term.
OK.
So back to the question that you asked Mauricio, which is what is he working on next? Yeah, yeah, yeah. What's the, what's the back end?
All the back end with that idea. I mean to me right now we only speak about having an activity creation. That activity creation will have a open user response that is going to be saved as a Jason BLOB or whatever.
Then whenever I send the results back to the viewer, I just need to send all bunch of blocks over there and the front end will take care of managing those results and.
Correct. So whatever input the the viewer wants to have, right? I did not the front end.
An activity, a viewer endpoint.
But that should not be happening on the phone.
So I agree it shouldn't be the responsibility of the activity and.
It should be the OR the participant endpoint. It should be the responsibility of the viewer endpoint. Yeah, to interpret the data. Yeah, the viewer endpoint should interpret the data and send to the front end with the front end.
That logic probably should not be like the logic of tallying up what needs to be tallied up probably should not be on the on the front end. So I maybe maybe we have a different interpretation of what the front end is then because we have like we have the admin panel.
Where we can layout what a session is and and and configuring the activities. Yeah, then we we have the.
The activity.
Which within it contains 2 views, the participant view and the viewer view. Yeah, and this we are going to have six of these, four of these, 20 of these. We'll have 20 different kinds of activities, any one of which could be assembled into a.
Session in any order with any configuration. OK, so question. So we're doing React on the front end. Do you see each type of activity as being a different React component or each type of activity being as a different React component that has been initialized with different parameters?
What do you think?
Say that again. Do you see? So a a session is gonna be configured to have different activities, right? And the different activities potentially are going to display their own data maybe a little bit differently.
Yeah. Do you see each activity, let's say there's an activity that's polling and there's an activity that's poker planning and there's an activity that's stumble. Do you see each one of these as being a different physically different React component or do you see them as being the same React component that?
Basically has different parameters and is being hydrated with different data. I believe they should be.
OK then.
Activity. Just give us a minute.
So let's say tomorrow I want to create AI am not a developer, I'm an admin for the application Caja de conflicto, right? And I want to create a new activity.
You can't, no. I believe that was, yeah, to create a React component. That was one of the discussions that we had yesterday, that whenever we will need to add a new activity, someone needs to come and edit the code. Then wait, we're not building a CMS on top of all.
So yeah, you said something interesting too. So you're saying that the admin portal is also a part of the activity, is that true or no?
Aware.
Yeah, like ask the question and then ask the question and what are the? I think what you all are saying is different from what I was thinking about, which is fine, but I think what you all are saying is the definition of a new activity is a development exercise. Oh, it totally is.
OK. And that's not at all what I was thinking. But yeah, OK, that that I think was the gap between why that why we we would need a structure under that circumstance and why we must not have that. That makes a fair idea. How long will the CMS? Yeah, it's not. It's not really a CMS, but I think it's a bigger conversation, but I think it's.
I I think it's fine for the for the building this in the next couple of days, I think that's fine.
Like the details of an activity, it's like, yes, we'll have an activity for multiple choice, we'll have an activity for live polling, all that stuff, right? But to define a new activity, yeah, you may have some, you may have sort of built in activities that are more flexible.
So for example, you could have a multiple choice activity and you could say for example in theory you could say hey that's good enough for playing poker, but you may also say planning poker specifically has time restrictions to the ability to.
Answer questions.
It needs to be able to like initiate, initiate the activity and then start the timer like they're specific. I think that's you all are talking about something that's a little bit more feature rich and specific in terms of how you manage different activities, which is fine.
And so one thing I think we still have to figure out a solution for is if if like right now we got user responses are completely up to the activity that's driving the participant view, the participant view says.
I'm gonna give you a pointing poker thing and you get to choose one of the cards and the user response will just say I chose 5. That's the response. It's a five. It might not even be Jason, but it could be. I hope it's Jason, but configuring what the questions are is the responsibility of the admin and the admin sits outside of the activity.
So like like how do we configure? I think the the activity just has three different components. It has a mapping component, it has a.
OK, what's the quality component and the viewer component participant? Thank you. OK, so that. So then the admin simply gets to to say I want to do a two, then a four, then a one.
And then it's like, great, all set. Let's go to A2. Use me to configure myself. Yep, my instance of myself. I'm like, OK, what do you want from me? Oh, you want me to give you a list of questions to ask the user? Or here are my 15 questions to ask the user. Yeah.
That goes into not the user inputs thing, but the session session ID.
Activity ID. I don't know what the model for that, but like there's gonna be a separate table for session configuration for session.
It says when we start a session of this, of this definition, like we take it from a class to an object. Yeah, we configured A2 with this set of questions. We configured A4 with these people to be. There's a type of, yeah, yeah, yeah. So there's a type of session and there's a type of.
Activity may be so like the session that you're having is OK, so let's use this example, right? The session that you're having is a Sprint planning session, the array of activities that you want to be able to have in that session. Right now the only one that we've thought about is planning poker, yeah.
And each planning booker instance is for a particular user story.
Yeah, yeah. Or maybe you guys can think about that while I go back to my IC stuff, but maybe for spring planning and planning poker, it doesn't really matter the name of the story. Like we don't have to complicate this and actually get the name of the story so that the name can be displayed.
On the viewer, it's just, hey, for the active story that we're all talking about, we've been talking about for the last 10 minutes. Yeah. What's your, what's your Fibonacci number for that? Sure. And then just take that and then move on to the next activity, right? Yeah, yeah, that's definitely an interpretation. And to that point, I even wonder.
If in a session you could just say, hey, I'm just gonna repeat this activity, but I'm not gonna tell you there's seven of them. I'm just gonna tell you it's this activity. Just keep repeating it. Yeah, cuz that's what happens in playing poker, right?
Sprint planning sessions is, hey, we might go through seven stories today. We might go through five stories today, exactly depending on how complex they are. So you don't know ahead of time if this session doesn't have a fixed number of activities in it. It's just the type of activity is this. Yep, and until I end my session, just keep going through the activities. Yeah, there's a number of different interpretations of that.
I would like you could layout all the stories you want point or you could just say I'm gonna as a viewer, I wanna have a text box so I can type the story we're working on and a button to clear the votes so that when I type in the news story and clear the votes, yeah, you know, yeah, or it could be in a completely different way like.
The nature of what the user response is completely changes. It's just simply I said 5. What I like related to that question. What I like about that is that because you're having a different a different React component for each type of activity, you can specifically.
Um.
Tailor the UX for that activity. So for example your example of hey, as the viewer for a plan for a Sprint planning session, I want to be able to just enter for every story. I just want to be very explicit. This is the story we're pointing now.
Boom post, right? And that can be very different from an activity, a session or an activity where the text of the activity is dictated by the.
Uh, admin. Yeah. Yeah. OK, cool. Cool. All right, good chat. Good chat. Now we're gonna get the transcript. Yep. Then we're gonna take that transcript and we're gonna crunch issues, new issues and uh.
And update docs.
