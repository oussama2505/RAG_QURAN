import { appStore } from '../stores/appStore';

type ShortcutHandler = (event: KeyboardEvent) => void;

interface Shortcut {
  key: string;
  description: string;
  handler: ShortcutHandler;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
}

const shortcuts: Shortcut[] = [];

export function registerShortcut(shortcut: Shortcut): void {
  shortcuts.push(shortcut);
}

export function unregisterShortcut(key: string): void {
  const index = shortcuts.findIndex(s => s.key === key);
  if (index !== -1) {
    shortcuts.splice(index, 1);
  }
}

export function initializeShortcuts(): void {
  window.addEventListener('keydown', handleKeyDown);
}

export function destroyShortcuts(): void {
  window.removeEventListener('keydown', handleKeyDown);
}

function handleKeyDown(event: KeyboardEvent): void {
  const matchingShortcut = shortcuts.find(shortcut => {
    return shortcut.key.toLowerCase() === event.key.toLowerCase() &&
      !!shortcut.ctrlKey === event.ctrlKey &&
      !!shortcut.altKey === event.altKey &&
      !!shortcut.shiftKey === event.shiftKey;
  });

  if (matchingShortcut) {
    event.preventDefault();
    matchingShortcut.handler(event);
  }
}

export function getRegisteredShortcuts(): Array<{
  key: string;
  description: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
}> {
  return shortcuts.map(({ key, description, ctrlKey, altKey, shiftKey }) => ({
    key,
    description,
    ctrlKey,
    altKey,
    shiftKey,
  }));
}