import {Button, Card,TextField, TextStyle, EmptyState, Layout, Page } from '@shopify/polaris';
import React, {Component, useState, useCallback} from 'react';
// import { Alert } from 'reactstrap';

class ShoppingList extends React.Component {
  render() {
    return (
      <div className="shopping-list">
        <h1>Shopping List for {this.props.name}</h1>
        <ul>
          <li>Instagram</li>
          <li>WhatsApp</li>
          <li>Oculus</li>
        </ul>
      </div>
    );
  }
}

class Square extends React.Component{
    constructor(props) {
    super(props);
    this.state = {
      value: 'button',
    };
  }

    render() {
        return (
            <button
                className="square"
                onClick={() => this.setState({value: 'X'})}
                >
                {this.state.value}
            </button>
        );
     }
}

class CustomText extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (

            <p>{this.props.message}</p>
        );
    }
}

class Clock extends Component{

    constructor(props) {
        super(props);
        this.state = {date: new Date()};
    }

    componentDidMount(){
        this.timerID = setInterval(() => this.tick(),1000);
    }

    componentWillUnmount(){
        clearInterval(this.timerID)
    }

    tick(){
        this.setState({
            date: new Date()
        });
    }

    render(){
        return(
            <div>
                <h1>Clock !!!</h1>
                <h2>Time: {this.state.date.toLocaleTimeString()}</h2>
            </div>
        )
    }
}

function WarningBanner(props){
    if (!props.warn){
        return null;
    }
    return (
        <div className="Warning">
            Warning!
        </div>
    )
}

class ToggleWarning extends Component {

    constructor(props) {
        super(props);
        this.state = {ShowWarning: true};
        this.ShowWarningButton = this.ShowWarningButton.bind(this);
    }

    ShowWarningButton(){
        this.setState(state => ({
            ShowWarning: !state.ShowWarning
        }));
    }

    render(){
        return(
            <div>
                <WarningBanner  warn={this.state.ShowWarning} />
                <Button onClick={this.ShowWarningButton} >
                    {this.state.ShowWarning? "Hide" : "Show"}
                </Button>
            </div>
        )
    }
}

function TestText(props){
    return <h1>Hello, {props.name}</h1>
}

function Avatar(props){
    return(
        <img className="Avatar" alt="failed"
    />
    )
}

function UserInfo(props){
    return(
        <div className="UserInfo">
            <div className="UserInfo-avatar">
                <Avatar />
            </div>
            <div className="UserInfo-name">
                <h1>Author 123</h1>
            </div>
        </div>
    )
}

function Comment(props){
    return(
        <div className="Comment">
            <UserInfo />
            <div className="CommentText">
                <p>This is a comment</p>
            </div>
            <div className="CommentDate">
                <p>{new Date().toLocaleTimeString()}</p>
            </div>
        </div>
    )
}

function ShowList(props){
    const numbers = props.numbers;
    const listItems = numbers.map((number) =>
        <li key={number.toString()}>
            {number} </li>
    );
    return (
        <ul>{listItems}</ul>
    );
}

class FlavorForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: 'coconut'};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    alert('Your favorite flavor is: ' + this.state.value);
    event.preventDefault();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label>
          Pick your favorite flavor:
          <select value={this.state.value} onChange={this.handleChange}>
            <option value="grapefruit">Grapefruit</option>
            <option value="lime">Lime</option>
            <option value="coconut">Coconut</option>
            <option value="mango">Mango</option>
          </select>
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

class NameForm extends Component{
    constructor(props) {
        super(props);
        this.state = {
            value: ''
        };
        this.handleOnchange = this.handleOnchange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleOnchange(event){
        this.setState({value: event.target.value});
    }

    handleSubmit(e){
        alert("a Name is submitted:"+ this.state.value);
        event.preventDefault();
    }

    render(){
        return(
            <div>
                <form onSubmit={this.handleSubmit}>
                    <label>Name:
                        <textarea value={this.state.value} onChange={this.handleOnchange} />
                    </label>
                    <input type="submit" value="submit" />
                </form>
            </div>
        )
    }
}

class LoginControl extends React.Component {
  constructor(props) {
    super(props);
    this.handleLoginClick = this.handleLoginClick.bind(this);
    this.handleLogoutClick = this.handleLogoutClick.bind(this);
    this.state = {isLoggedIn: false};
  }

  handleLoginClick() {
    this.setState({isLoggedIn: true});
  }

  handleLogoutClick() {
    this.setState({isLoggedIn: false});
  }

  render() {
    const isLoggedIn = this.state.isLoggedIn;
    let button;
    if (isLoggedIn) {
        button = <Button onClick={this.handleLogoutClick} >Log Out</Button>;
    } else {
        button = <Button onClick={this.handleLoginClick} >Log In</Button>;
    }

    return (
      <div>
        <p>The user is <b>{isLoggedIn ? 'currently' : 'not'}</b> logged in.</p>
        {button}
      </div>
    );
  }
}
const numbers = [1, 2, 3, 4, 5];
class Hello extends React.Component {


    constructor(props){
        super(props);
        this.state = {
            message:'Welcome to code 101'
        };
    }

    render() {
        return (
            <Page>
                <Layout>
                    <h1> {this.state.message}< /h1>
                    <h2> 123abc </h2>
                    <h2> It is {new Date().toLocaleTimeString()}. </h2>
                    <CustomText message={this.state.message} />
                    <ShoppingList name='Thinh'/>
                        <Square value='Abc123'/>
                        <div>
                            <TestText name='Thinh123'/><br />
                            <TestText name='Thinh1'/><br />
                            <TestText name='Thinh12'/><br/>
                        </div><br />
                        <Comment />
                        <Clock />
                        <LoginControl />
                        <ToggleWarning />
                        <ShowList numbers={numbers}/>
                        <NameForm />
                        <FlavorForm />
                </Layout>
            </Page>
        )
    }

}

const Index = () => (
    <Hello />
);

export default Index;


