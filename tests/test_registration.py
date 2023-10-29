import pytest
from app.src.auth import register
from app.src.models import User, db

from flask import Flask, request, redirect, url_for

# TODO