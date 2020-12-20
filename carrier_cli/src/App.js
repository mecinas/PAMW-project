import React, { PureComponent } from 'react';
import axios from 'axios';
import DropdownEl from './elements/DropdownEl';
import { Table } from 'reactstrap';
import jwt from 'jsonwebtoken';
//TODO
//Stworzenie POST zmiana statusu paczki
//Uporządkowanie .env tylko tam gdzie jest potrzebne

export default class App extends PureComponent {
  is_authorized = true
  state = {
    "all_packages": []
  }
  createToken() {
    let key = process.env.REACT_APP_JWT_SECRET;
    let payload = {
      "permission_as": "carrier"
    }
    let token = jwt.sign(payload, key)
    return token
  }
  token = this.createToken()


  downloadPackages() {
    let path = 'https://murmuring-springs-10121.herokuapp.com/root/carrier/dashboard'
    axios.get(path, {
      params: {
        "cookie": this.token
      }
    }).then(resp => {
      if (resp.data.data.is_authorized)
        this.setState({ "all_packages": resp.data.data.all_packages })
      else
        this.is_authorized = false
    })
  }

  send_post_request = (state, index_of_row, username) => {
    let path = 'https://murmuring-springs-10121.herokuapp.com/root/carrier/dashboard'
    axios.put(path, null, {
      params: {
        "user": username,
        "index_of_row": index_of_row,
        "cookie": this.token,
        "state": state
      }
    })
  }

  render() {
    if (!this.is_authorized) {
      return <p>Brak dostępu, 404</p>
    }
    else {
      this.downloadPackages()
      let start_packages = this.state.all_packages
      let packages = start_packages.map((single_package) => {
        return (
          <tr>
            <td>{single_package.sender_name}</td>
            <td>{single_package.adressee_name}</td>
            <td>{single_package.storeroom_id}</td>
            <td>{single_package.size}</td>
            <td>{single_package.state}</td>
            <td>
              <DropdownEl send_post_request={this.send_post_request} index_of_row={single_package.id}
               username={single_package.sender_name}/>
            </td>
          </tr>
        )
      });
      return (
        <div className="content_container">
          <Table>
            <thead>
              <tr>
                <th>Nazwa nadawcy</th>
                <th>Nazwa adresata</th>
                <th>Skrytka docelowa</th>
                <th>Rozmiar paczki</th>
                <th>Stan</th>
                <th>Zmień stan</th>
              </tr>
            </thead>
            <tbody>
              {packages}
            </tbody>
          </Table>
        </div>
      );
    }
  }
}
